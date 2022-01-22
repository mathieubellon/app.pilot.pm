from django.http import HttpResponseBadRequest
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from pilot.activity_stream.jobs import create_activity
from pilot.activity_stream.models import Activity
from pilot.items.models import Item
from pilot.itemsfilters.models import SavedFilter
from pilot.notifications import emailing, notify
from pilot.sharings.api.filters import SharingFilter
from pilot.sharings.api.serializers import SharedItemSerializer, SharingSerializer
from pilot.sharings.api.serializers_base import ItemFeedbackSerializer
from pilot.sharings.models import Sharing, SharingStatus, SharingType
from pilot.utils import api as api_utils
from pilot.utils.perms import filter_items_for_sharing


class SharingListPagination(api_utils.PilotPageNumberPagination):
    page_size = 25


class SharingsViewset(
    api_utils.ActivityModelMixin,
    api_utils.BulkActionMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Sharings are handled as immutable, so there's no update API.
    There's neither the delete API, because when the users want to remove a Sharing,
    we keep an instance anyway with only the token, to avoid showing 404 to the recipient.
    """

    serializer_class = SharingSerializer
    permission_classes = [
        api_utils.DeskPermission
    ]
    filter_class = SharingFilter
    lookup_field = 'token'
    activity_create_verb = Activity.VERB_SHARED

    def get_queryset(self):
        return (
            Sharing.objects
            # request.desk will be set correctly by the SharedApiMixin
            .filter(desk=self.request.desk)
            .filter(deactivated=False)
            .select_related('project', 'channel', 'saved_filter')
            .prefetch_related('feedbacks')
        )

    # ===================
    # Create / Update
    # ===================

    def perform_create(self, serializer):
        # Ensure the user isn't trying to share the filter of someone else
        data = serializer.validated_data
        if data.get('type') in [SharingType.LIST, SharingType.CALENDAR]:
            saved_filter = get_object_or_404(SavedFilter, id=data.get('saved_filter_id'))
            if self.request.user != saved_filter.user:
                raise PermissionDenied(_("Vous ne pouvez partager que vos filtres"))

        sharing = serializer.save(
            desk=self.request.desk,
            created_by=self.request.user
        )

        if sharing.email:
            emailing.send_sharing(sharing)

    # ===================
    # Activity
    # ===================

    def get_activity_create_target(self, sharing):
        return sharing.get_target()

    def get_activity_create_action_object(self, sharing):
        return sharing

    # ===================
    # Custom routes
    # ===================

    @action(detail=False, pagination_class=SharingListPagination)
    def paginated(self, *args, **kwargs):
        return self.list(*args, **kwargs)

    @action(detail=True, methods=['POST'])
    def deactivate(self, request, token):
        sharing = self.get_object()
        deactivated_sharing = self.action_deactivate(sharing)
        return Response(self.get_serializer(deactivated_sharing).data)

    # ===================
    # Actions
    # ===================

    def get_bulk_action_handlers(self):
        return {
            'deactivate': self.action_deactivate,
        }

    def action_deactivate(self, sharing, params={}):
        deactivated_sharing = Sharing(
            id=sharing.id,
            token=sharing.token,
            deactivated=True,
            created_by=sharing.created_by
        )
        deactivated_sharing.save()
        return deactivated_sharing


class SharedItemFeedbackViewset(
    api_utils.SharedApiMixin,
    viewsets.mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ItemFeedbackSerializer
    permission_classes = [
        AllowAny
    ]

    def perform_create(self, serializer):
        sharing = self.sharing

        # Only sharings sent to a specific recipient can have feedbacks
        if not sharing.email:
            return HttpResponseBadRequest("This sharing cannot have feedbacks because it has no recipient email")

        feedback = serializer.save(
            desk=sharing.desk,
            sharing=sharing
        )
        notify.notify_sharing_feedback(feedback)

        if feedback.status == SharingStatus.APPROVED:
            verb = Activity.VERB_FEEDBACK_APPROVED
        elif feedback.status == SharingStatus.REJECTED:
            verb = Activity.VERB_FEEDBACK_REJECTED
        create_activity(
            actor=sharing.email,
            desk=sharing.desk,
            verb=verb,
            target=feedback.item,
            action_object=feedback
        )


class SharedItemRetrieve(api_utils.SharedApiMixin,
                         generics.RetrieveAPIView):
    serializer_class = SharedItemSerializer

    def get_queryset(self):
        queryset = (
            Item.objects
            # request.desk will be set correctly by the SharedApiMixin
            .filter(desk=self.sharing.desk)
            .select_related('item_type', 'project')
            .prefetch_related('channels')
        )

        # Ensure that the item is a member of the sharing
        return filter_items_for_sharing(queryset, self.sharing)
