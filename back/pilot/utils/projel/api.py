from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action

from pilot.accounts.usage_limit import UsageLimitReached
from pilot.activity_stream.comment import create_comment_and_activity
from pilot.notifications import notify
from pilot.activity_stream.models import Activity
from pilot.activity_stream.jobs import create_activity
from pilot.utils import api as api_utils, states
from pilot.assets import utils as assets_utils


class ProjelListPagination(api_utils.PilotPageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'


class ProjelViewSet(api_utils.ActivityModelMixin,
                     mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    A viewset to work with Projels endpoint
    """
    permission_classes = [
        api_utils.DeskPermission
    ]
    pagination_class = ProjelListPagination
    default_ordering = '-updated_at'

    list_actions = ['active', 'idea', 'closed']

    # ===================
    # Declare Viewset methods
    # ===================

    def get_queryset(self):
        queryset = (
            self.base_queryset
            .filter(desk=self.request.desk)
            .filter_by_permissions(self.request.user)
            # Default ordering, that may be overrided by the query params
            .order_by(self.default_ordering)
        )

        if self.action == 'choices':
            # Projel choices won't serialize any related, don't add overhead
            return queryset
        elif self.action in self.list_actions:
            return queryset.list_api_prefetch()
        else:
            return queryset.detail_api_prefetch()

    # ===================
    # Create / Update
    # ===================

    def perform_create(self, serializer):
        assets_data = self.request.data.pop('assets', [])

        projel = serializer.save(
            desk=self.request.desk,
            created_by=self.request.user
        )

        assets_utils.link_uploaded_assets(self.request, projel, assets_data)

    # ===================
    # Custom routes
    # ===================

    @action(detail=True, methods=['PUT'])
    def close(self, request, *args, **kwargs):
        projel = self.get_object()
        self.action_close(projel)
        return Response(self.get_serializer(projel).data)

    @action(detail=True, methods=['PUT'])
    def reopen(self, request, *args, **kwargs):
        projel = self.get_object()
        self.action_reopen(projel)
        return Response(self.get_serializer(projel).data)

    @action(detail=True, methods=['PUT'])
    def soft_delete(self, request, *args, **kwargs):
        """
        Projel soft delete consists in "hiding" the projel, not deleting it from DB.
        Soft deleted projels can be restored.
        """
        if request.user.permissions.is_restricted_editor:
            raise PermissionDenied()

        projel = self.get_object()
        self.action_hide(projel)
        return Response(self.get_serializer(projel).data)

    @action(detail=True, methods=['PUT'])
    def update_state(self, request, *args, **kwargs):
        comment_content = request.data.pop('comment')
        notify_author = request.data.pop('notify_author')
        with transaction.atomic():
            instance = self.get_object()
            old_state = str(instance.state)

            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            try:
                self.perform_update(serializer)
            except UsageLimitReached as e:
                return Response(str(e), status=status.HTTP_403_FORBIDDEN)

            # Create the comment
            create_comment_and_activity(
                instance=instance,
                comment_content=comment_content,
                user=self.request.user
            )

            # Determine the activity verb and user message for notification
            activity_verb = None
            is_accepted = None
            new_state = str(instance.state)
            if old_state == states.STATE_IDEA:
                if new_state == states.STATE_ACTIVE:
                    activity_verb = Activity.VERB_ACCEPTED_IDEA
                    is_accepted = True
                elif new_state == states.STATE_REJECTED:
                    is_accepted = False
                    activity_verb = Activity.VERB_REJECTED_IDEA
            if old_state == states.STATE_REJECTED and new_state == states.STATE_IDEA:
                activity_verb = Activity.VERB_CANCELLED_REJECTION
            if old_state == states.STATE_CLOSED and new_state == states.STATE_ACTIVE:
                activity_verb = Activity.VERB_REOPENED

            # Notify author
            if notify_author and (is_accepted is not None):
                notify.notify_idea_validation(instance, is_accepted)

            # Send Activity Stream
            create_activity(
                actor=request.user,
                desk=request.desk,
                verb=activity_verb,
                target=instance
            )

        return Response(serializer.data)

    # ===================
    # Actions
    # ===================

    def action_close(self, projel, params={}):
        projel.state = states.STATE_CLOSED
        projel.closed_at = timezone.now()
        projel.updated_by = self.request.user
        projel.save()
        self.create_activity(target=projel, verb=Activity.VERB_CLOSED)

    def action_reopen(self, projel, params={}):
        projel.state = states.STATE_ACTIVE
        projel.closed_at = None
        projel.updated_by = self.request.user
        projel.save()
        self.create_activity(target=projel, verb=Activity.VERB_REOPENED)

    def action_hide(self, projel, params={}):
        with transaction.atomic():
            projel.hide(user=self.request.user)
            for asset in projel.assets.filter(in_media_library=False):
                asset.hide(user=self.request.user)
            self.create_activity(target=projel, verb=Activity.VERB_HIDDEN)
