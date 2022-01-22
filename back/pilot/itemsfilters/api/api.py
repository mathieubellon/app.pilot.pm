from django.db.models import Q
from django.utils.translation import ugettext as _

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework import status

from pilot.itemsfilters.api.filters import InternalSharedFilterFilter, SavedFilterFilter
from pilot.itemsfilters.api.serializers import InternalSharedFilterSerializer, SavedFilterSerializer
from pilot.itemsfilters.jobs import ItemFilterXLSExportJob
from pilot.itemsfilters.models import InternalSharedFilter, SavedFilter
from pilot.notifications.notify import get_mentionned_users, notify_internal_shared_filter
from pilot.utils import api as api_utils


class SavedFilterViewSet(viewsets.ModelViewSet):
    serializer_class = SavedFilterSerializer
    filter_class = SavedFilterFilter
    permission_classes = [
        api_utils.DeskPermission
    ]
    default_ordering = 'title'

    def get_queryset(self):
        return (
            SavedFilter.objects
            .filter(desk=self.request.desk)
            .filter(
                Q(user=self.request.user)
                |
                Q(internal_shared_filters__users=self.request.user)
            )
            # Default ordering, that may be overrided by the query params
            .order_by(self.default_ordering)
            .distinct()
        )

    def perform_create(self, serializer):
        serializer.save(
            desk=self.request.desk,
            user=self.request.user,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, saved_filter):
        if self.request.user != saved_filter.user:
            raise PermissionDenied(_("Seul le créateur du filtre peut le supprimer"))

        saved_filter.delete()

    @action(detail=True, methods=['PUT'])
    def export(self, request, *args, **kwargs):
        saved_filter = self.get_object()
        ItemFilterXLSExportJob.launch_r(self.request, saved_filter, timeout='30m')
        return Response(status=status.HTTP_202_ACCEPTED)


class InternalSharedFilterViewSet(viewsets.ModelViewSet):
    serializer_class = InternalSharedFilterSerializer
    filter_class = InternalSharedFilterFilter
    permission_classes = [
        api_utils.DeskPermission
    ]

    def get_queryset(self):
        return InternalSharedFilter.objects.filter(
            saved_filter__desk=self.request.desk
        )

    def perform_create(self, serializer):
        data = serializer.validated_data
        saved_filter = SavedFilter.objects.get(id=data['saved_filter_id'])

        if self.request.desk != saved_filter.desk:
            raise PermissionDenied(_("Permission refusée"))
        if self.request.user != saved_filter.user:
            raise PermissionDenied(_("Vous ne pouvez partager que vos filtres"))

        users = get_mentionned_users(
            content=data['message'],
            instance=None,
            desk=self.request.desk
        )

        if not users:
            raise ValidationError(_("Merci de renseigner au moins un utilisateur"))

        shared_filter = serializer.save(
            created_by=self.request.user,
            users=users
        )

        notify_internal_shared_filter(shared_filter)
