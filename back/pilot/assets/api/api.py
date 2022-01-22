import json
import logging

from django.db.models import Prefetch
from django.conf import settings
from django.db import transaction
from django.http import HttpResponseForbidden
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.utils.translation import ugettext as _

from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.status import HTTP_201_CREATED

from pilot.assets.api.filters import AssetFilter, AssetRightFilter
from pilot.assets.api.serializers import AssetRightSerializer, AssetSerializer, UrlAssetSerializer
from pilot.assets.models import Asset, AssetRight
from pilot.notifications.models import Reminder
from pilot.realtime.broadcasting import broadcaster
from pilot.utils import api as api_utils
from pilot.activity_stream.models import Activity
from pilot.assets.utils import create_asset, get_uploaded_file_attributes, start_transloadit_conversion, \
    start_transloadit_assets_zip
from pilot.utils.s3 import get_s3_signature_v4

logger = logging.getLogger(__name__)


class AssetListPagination(api_utils.PilotPageNumberPagination):
    page_size = 30


class AssetViewSet(api_utils.GenericObjectMixin,
                   api_utils.ActivityModelMixin,
                   viewsets.ModelViewSet):
    permission_classes = [
        api_utils.DeskPermission
    ]
    pagination_class = AssetListPagination
    serializer_class = AssetSerializer
    filter_class = AssetFilter
    extra_filters = {}
    default_ordering = '-updated_at'

    list_actions = ['list', 'linked', 'library']

    def get_queryset(self):
        queryset = (
            Asset.objects
            .filter(desk=self.request.desk, **self.extra_filters)
            .prefetch_related('asset_rights')
            # Default ordering, that may be overrided by the query params
            .order_by(self.default_ordering)
        )

        if self.request.user.is_authenticated:
            # VERY IMPORTANT : Filter the reminders to keep only those of the current user
            # ALso optimize by prefeteching the M2M relationship.
            queryset = queryset.prefetch_related(
                Prefetch('asset_rights__reminders', queryset=Reminder.objects.filter(user=self.request.user))
            )

        return queryset

    # Temporary "Creation" through assetId instead of UUID
    def create(self, request, *args, **kwargs):
        self.kwargs['pk'] = self.request.data['assetId']
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            self.perform_create(serializer)
            self.create_activity_for_create(serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        asset = create_asset(self.request, serializer, self.request.data)

        content_type_id = self.request.data.get('content_type_id', None)
        # If there is no Content_type_id in POST data we assume we are not creating the asset
        # from an item but from the main list.
        if content_type_id:
            linked_object = self.get_generic_object()
            linked_object.assets.add(asset)

            self.create_activity(
                verb=Activity.VERB_ASSET_LINKED,
                target=linked_object,
                action_object=asset
            )

        return asset

    def perform_update(self, serializer):
        asset = serializer.instance
        old_name = asset.name
        file_changed = self.request.data.get('fileChanged', False)

        update_kwargs = dict(
            updated_by=self.request.user,
        )

        # If the file changed, bump the version number, and start a new conversion
        if file_changed:
            # We need to update the asset field immediately to update the file name we send to transloadit
            asset.version = asset.version+1
            # New version, so erase previous conversions informations
            asset.conversions['version'] = asset.version

            update_kwargs.update(dict(
                file=self.request.data['file'],
                version=asset.version
            ))

            if 'fileName' in self.request.data:
                update_kwargs.update(get_uploaded_file_attributes(self.request.data['fileName']))

        serializer.save(**update_kwargs)

        if file_changed:
            conversion_data = start_transloadit_conversion(serializer.instance)
            asset.update_conversion_data(conversion_data)
            asset.save()

        elif old_name != asset.name:
            # If the title changed, update the download name in S3
            asset.update_s3_filename()

        return asset

    def perform_destroy(self, asset):
        """
        We don't actually destroy the instance, but set its "hidden" flag to True
        """
        if self.request.user.permissions.is_restricted_editor:
            raise PermissionDenied()

        asset.hide(user=self.request.user)

        content_type_id = self.request.data.get('content_type_id', None)
        if content_type_id:
            self.create_activity(
                verb=Activity.VERB_ASSET_UNLINKED,
                target=self.get_generic_object(),
                action_object=asset
            )

    @action(detail=False, extra_filters={'in_media_library': True})
    def library(self, request):
        """
        Returns the list of assets available in the media library
        """
        return self.list(request)

    # ===================
    # Linked assets zone
    # ===================

    @action(detail=False, pagination_class=None, url_path='linked/(?P<content_type_id>\d+)/(?P<object_id>\d+)')
    def linked(self, request, *args, **kwargs):
        """
        List of the assets linked to a generic object

        The target object is looked up by the two parameters in the url :
         * content_type_id : The id of the content_type
         * object_id : The id of the object of this content_type
        """
        linked_object = self.get_generic_object()
        queryset = linked_object.assets.order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def link(self, request, *args, **kwargs):
        """
        Link an asset to a target generic object.

        The asset to link is determined by the url (/api/assets/{asset_pk})

        The target object is looked up by the two POST parameters :
         * content_type_id : The id of the content_type
         * object_id : The id of the object of this content_type

        Returns a 404 if no target object can be found.
        Send an activity stream to the target generic object.
        """
        asset = self.get_object()

        if not asset.in_media_library:
            return HttpResponseBadRequest(f"Cannot link : asset {asset} is not in the media library")

        linked_object = self.get_generic_object()

        with transaction.atomic():
            linked_object.assets.add(asset)

            self.create_activity(
                verb=Activity.VERB_ASSET_LINKED,
                target=linked_object,
                action_object=asset
            )

        return HttpResponse()

    @action(detail=True, methods=['POST'])
    def unlink(self, request, *args, **kwargs):
        """
        Remove the link between an asset and a a target generic object.

        The asset to unlink is determined by the url (/api/assets/{asset_pk})

        The target object is looked up by the two POST parameters :
         * content_type_id : The id of the content_type
         * object_id : The id of the object of this content_type

        Returns a 404 if no target object can be found.
        Send an activity stream to the target generic object.

        Raises a Http Error "Bad Request" if the asset is not linked to the target object.
        """
        asset = self.get_object()
        linked_object = self.get_generic_object()

        if asset not in linked_object.assets.all():
            return HttpResponseBadRequest(f"Cannot unlink : asset {asset} is not linked to {linked_object}")

        with transaction.atomic():
            linked_object.assets.remove(asset)

        self.create_activity(
            verb=Activity.VERB_ASSET_UNLINKED,
            target=linked_object,
            action_object=asset
        )

        return HttpResponse()

    @action(detail=False, methods=['POST'], url_path='create_url_asset/(?P<content_type_id>\d+)/(?P<object_id>\d+)')
    def create_url_asset(self, request, *args, **kwargs):
        linked_object = self.get_generic_object()

        serializer = UrlAssetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the asset.
        asset = serializer.save(
            desk=self.request.desk,
            created_by=self.request.user
        )

        # Linking created asset to current object
        linked_object.assets.add(asset)

        full_serializer = self.get_serializer(asset)
        return Response(full_serializer.data)

    # ===================
    # S3 Signature zone
    # ===================

    @action(detail=False, methods=['POST'])
    def get_s3_signature(self, request, *args, **kwargs):
        if settings.ON_DEMO_SITE:
            return HttpResponseForbidden(_("L'upload de fichier est désactivé sur le site de démo"))

        file_name = request.data.get('fileName')
        file_attributes = get_uploaded_file_attributes(file_name)

        content_type = request.data.get('contentType')
        asset_id = request.data.get('assetId', None)

        if asset_id:
            # We're updating the asset
            asset = Asset.objects.get(pk=asset_id)
            # If we're updating, then we need to increment the version for the file name in asset.originalpath
            asset.version += 1
            # And we also need to update the extension if it changed for the file name in asset.originalpath
            asset.extension = file_attributes['extension']
        else:
            created_by = request.user if request.user.is_authenticated else None
            # We're creating the asset
            asset = Asset.objects.create(
                desk=request.desk,
                created_by=created_by,
                in_media_library=False,
                **file_attributes
            )

        # Code for UUID naming, to be used later
        # if asset_id:
        #     #Update context
        #     asset = Asset.objects.get(pk=asset_id)
        #     assset_uuid = asset.uuid
        #     key = 'medias/{deskId}/{UUID}_original'.format(
        #         deskId=request.desk.id,
        #         UUID=assset_uuid
        #     )
        # else:
        #     assset_uuid = uuid.uuid4()
        #     # Create new uuid before asset is created
        #     # Asset will be created later, after upload to s3, with this uuid.
        #     # If things break during the process we can end up with orphan objects on s3.
        #     # So we need to write a cleaning script
        #     key = 'medias/{deskId}/{UUID}_original'.format(
        #         deskId=request.desk.id,
        #         UUID=assset_uuid
        #     )


        # if desk:
        #     # Come from authenticated user
        #     key = 'medias/{deskId}/{UUID}'.format(
        #         deskId=request.desk.id,
        #         UUID=uuid.uuid4()
        #     )
        # else:
        #     # Come from anonymous user
        #     key = 'tmp/{0}'.format(hmac.new(unique.bytes, digestmod=sha1).hexdigest())

        signature_data = get_s3_signature_v4(asset.originalpath, content_type, file_name)
        signature_data['assetId'] = asset.id

        return HttpResponse(json.dumps(signature_data), content_type="application/json")


    # ===================
    # Transloadit zone
    # ===================

    @action(detail=True, methods=['POST'])
    def start_conversion(self, request, *args, **kwargs):
        """
        File conversion using transloadit.com services
        Use it to generate thumbnails for asset

        :return: Transloadit response
        """
        asset = self.get_object()

        asset.conversions = {
            "version": asset.version,
            "conversionData": start_transloadit_conversion(asset)
        }

        # TODO : Handle errors + Handle new conversion for new version case ('force' or 'reset' parameter)

        asset.save()

        serializer = self.get_serializer(asset)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], authentication_classes=[], permission_classes=[AllowAny])
    def notify_transloadit(self, request, pk):
        """Endpoint transloadit.com notification system will call to notify
        app once conversion work is done"""
        logger.info(f"Start handling transloadit notification")

        try:
            if 'transloadit' not in request.data:
                logger.info("transloadit key is not in the request params")
                return HttpResponseBadRequest("403 Forbidden")

            # TODO : Check signature from TL.com
            # if 'signature' in request.POST:

            # import hmac
            # import hashlib

            # send_signature = request.POST['signature']
            # assembly_params = request.POST['transloadit']
            #     print assembly_params

            #     home_signature = hmac.new(settings.TRANSLOADIT_AUTH_KEY, json.dumps(assembly_params), hashlib.sha1).hexdigest()

            #     print "home signature"
            #     print home_signature
            #     print "send signature"
            #     print send_signature

            #     if home_signature == send_signature:
            #         print "SIGNATURE OK, let it in"
            #     else:
            #         print "SIgnature MISMATCH, block door"
            # else:
            #     pass

            asset = get_object_or_404(Asset, pk=pk)

            logger.info("transloadit notification for asset {0}".format(asset.id))

            conversion_data = json.loads(request.POST['transloadit'])
            asset.update_conversion_data(conversion_data)
            asset.save()

            broadcaster.broadcast_asset_conversion_status(asset)

            assembly_id = conversion_data['assembly_id']
            if 'error' in conversion_data:
                logger.error(
                    'Transloadit assembly {assemblyid} for asset {assetpk} is in error'
                     ''.format(assemblyid=assembly_id, assetpk=asset.id),
                     exc_info=True
                )

            elif 'ok' not in conversion_data:
                logger.error(
                    'Transloadit assembly {assemblyid} for asset {assetpk} conversion data is incorrect'
                     ''.format(assemblyid=assembly_id, assetpk=asset.id),
                    exc_info=True
                )

            return HttpResponse()

        finally:
            logger.info(f"End handling transloadit notification")

    @action(detail=False, methods=['POST'])
    def start_zip(self, request, *args, **kwargs):
        """
        File archiving in a zip, using transloadit.com services

        The target object is looked up by the two POST parameters :
         * content_type_id : The id of the content_type
         * object_id : The id of the object of this content_type

        :return: Transloadit response
        """
        linked_object = self.get_generic_object()
        transloadit_response = start_transloadit_assets_zip(linked_object.assets.all())
        return Response(transloadit_response)


class AssetRightViewSet(api_utils.ActivityModelMixin,
                        viewsets.ModelViewSet):
    serializer_class = AssetRightSerializer
    filter_class = AssetRightFilter
    permission_classes = [
        api_utils.DeskPermission
    ]

    def get_queryset(self):
        queryset = AssetRight.objects.filter(desk=self.request.desk)

        if self.request.user.is_authenticated:
            # VERY IMPORTANT : Filter the reminders to keep only those of the current user
            # ALso optimize by prefeteching the M2M relationship.
            queryset = queryset.prefetch_related(
                Prefetch('reminders', queryset=Reminder.objects.filter(user=self.request.user))
            )

        return queryset


    # ===================
    # Create / Update
    # ===================

    def perform_create(self, serializer):
        return serializer.save(
            desk=self.request.desk,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
