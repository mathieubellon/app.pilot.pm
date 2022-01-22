import datetime

from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.translation import ugettext as _

from rest_framework import generics, status, viewsets, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action

from pilot.accounts.usage_limit import ItemUsageLimit, UsageLimitReached
from pilot.activity_stream.comment import create_comment_and_activity
from pilot.item_types.models import ItemType
from pilot.items.api.filters import ItemFilter
from pilot.items.api.light_serializers import EditSessionLightSerializer
from pilot.items.api.serializers import EditSessionSerializer, ItemCalendarSerializer, ItemInaccessibleSerializer, \
    ItemListSerializer, \
    ItemSerializer
from pilot.items.jobs import AllItemsXLSExportJob
from pilot.items.models import EditSession, Item
from pilot.itemsfilters.models import SavedFilter

from pilot.activity_stream.models import Activity
from pilot.notifications.models import Reminder
from pilot.pilot_users.api.serializers import PilotUserLightSerializer
from pilot.realtime.broadcasting import broadcaster
from pilot.realtime.items import ItemContentUpdater
from pilot.utils import api as api_utils, diff, states
from pilot.utils.copy_utils import copy_item
from pilot.utils.perms.private_items import user_can_access_item
from pilot.utils.projel.hierarchy import HierarchyConsistencyJob, apply_picked_channels, projels_for_item


class ItemPagination(api_utils.PilotPageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'


class ItemViewSet(api_utils.ActivityModelMixin,
                  api_utils.BulkActionMixin,
                  mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """
    ViewSet for item manipulation
    """
    base_queryset = Item.objects
    filter_class = ItemFilter
    default_ordering = '-updated_at'
    pagination_class = ItemPagination
    permission_classes = [
        api_utils.DeskPermission
    ]

    # Tells if this is a request for a calendar view
    # By default, filtering on the date is done against the publication task only
    # If is_calendar is set to True,
    # then all tasks are used for the lookup, with an OR.
    # In this case, all items with any task.deadline matching the lookup will be returned
    is_calendar = False

    list_actions = ['list', 'trash_list', 'shared_list', 'list_for_project', 'list_for_channel']

    # ===================
    # Declare Viewset methods
    # ===================

    def check_object_permissions(self, request, item):
        """
        Restrict access to private items to allowed users only
        """
        super(ItemViewSet, self).check_object_permissions(request, item)

        # Restrict access to private items
        if not user_can_access_item(request, item) and self.request.method != 'GET':
            raise PermissionDenied(_("Cet item est privé"))

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()

        if self.is_calendar:
            return ItemCalendarSerializer(*args, **kwargs)
        elif self.action == 'create':
            if 'item_type_id' in self.request.data:
                kwargs['item_type'] = ItemType.objects.get(
                    id=self.request.data['item_type_id'],
                    desk=self.request.desk
                )
            return ItemSerializer(*args, **kwargs)
        elif self.action in self.list_actions:
            return ItemListSerializer(*args, **kwargs)
        else:
            Serializer = ItemSerializer
            if args:
                item = args[0]
                if not user_can_access_item(self.request, item):
                    Serializer = ItemInaccessibleSerializer

            return Serializer(*args, **kwargs)

    def get_queryset(self):
        """
        Limit visible items to the current desk, and to restricted editor if applicable
        """
        queryset = self.base_queryset.filter(desk=self.request.desk).filter_by_permissions(self.request.user)

        if self.action in self.list_actions or self.is_calendar:
            queryset = queryset.list_api_prefetch()
        else:
            # We'll need the `json_content` field, don't defer it.
            queryset = queryset.with_content().annotate_version().detail_api_prefetch()

        if self.request.user.is_authenticated:
            # VERY IMPORTANT : Filter the reminders to keep only those of the current user
            # ALso optimize by prefeteching the M2M relationship.
            queryset = queryset.prefetch_related(
                Prefetch('tasks__reminders', queryset=Reminder.objects.filter(user=self.request.user))
            )

        if self.action in self.list_actions:
            # Default ordering, that may be overrided by the query params
            queryset = queryset.order_by(self.default_ordering)
            queryset = self.limit_queryset_in_time(queryset)

        if self.is_calendar:
            queryset = self.limit_queryset_in_time(queryset)
            queryset = queryset.filter(Q(project=None) | Q(project__state=states.STATE_ACTIVE))
            queryset = queryset.distinct()

        return queryset

    # ===================
    # Create / Update
    # ===================

    def perform_create(self, serializer):
        save_kwargs = {}

        if 'copied_from' in self.request.data:
            copied_from = get_object_or_404(Item, pk=self.request.data['copied_from'])
            save_kwargs['copied_from'] = copied_from
            save_kwargs['assets'] = copied_from.assets.all()
            save_kwargs['tags'] = copied_from.tags.all()
            self.activity_create_verb = Activity.VERB_COPIED
            self.activity_create_action_object = copied_from

        item = serializer.save(
            desk=self.request.desk,
            created_by=self.request.user,
            updated_by=self.request.user,
            last_editor=self.request.user.id,
            last_edition_datetime=timezone.now(),
            **save_kwargs
        )

        apply_picked_channels(item, self.request.data.get('picked_channels'))

        HierarchyConsistencyJob.launch_for_item(self.request, item)

    def perform_update(self, serializer):
        item = serializer.instance

        projels_before = projels_for_item(item)

        update_kwargs = dict(
            updated_by=self.request.user,
        )

        if not item.frozen and serializer.validated_data.get('frozen'):
            update_kwargs.update(dict(
                frozen_at=timezone.now(),
                frozen_by=self.request.user,
            ))
            self.activity_update_verb = Activity.VERB_FROZEN

        if item.frozen and serializer.validated_data.get('frozen') is False:
            update_kwargs.update(dict(
                frozen_at=None,
                frozen_by=None,
                frozen_message=None
            ))
            self.activity_update_verb = Activity.VERB_UNFROZEN

        serializer.save(**update_kwargs)

        apply_picked_channels(item, self.request.data.get('picked_channels'))

        broadcaster.broadcast_item(item.id, self.request.user.id)

        projels_after = projels_for_item(serializer.instance)
        # Make a symmetric difference between the two sets, to update only the affected projels ( added or removed )
        affected_projels = projels_before ^ projels_after
        if affected_projels:
            HierarchyConsistencyJob.launch_r(self.request, affected_projels)

        # Fetch a fresh Item instance, so the serializer have up to date data for its nested serializers
        # which may have been updated.
        serializer.instance = self.get_queryset().get(id=item.id)

    # ===================
    # Custom routes
    # ===================

    def retrieve(self, request, *args, **kwargs):
        '''
        We can retrieve any accessible items : idea, trash, confirmed...
        '''
        self.base_queryset = Item.accessible_objects
        return super(ItemViewSet, self).retrieve(request, *args, **kwargs)

    @action(detail=False, base_queryset=Item.in_trash_objects)
    def trash_list(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(detail=False, is_calendar=True, pagination_class=None)
    def calendar(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(detail=False, url_path='for_project/(?P<project_id>\d+)')
    def list_for_project(self, request, *args, **kwargs):
        request.project_id = kwargs['project_id']
        self.base_queryset = Item.objects.filter(project=kwargs['project_id'])
        return self.list(request, *args, **kwargs)

    @action(detail=False, url_path='for_channel/(?P<channel_id>\d+)')
    def list_for_channel(self, request, *args, **kwargs):
        request.channel_id = kwargs['channel_id']
        self.base_queryset = Item.objects.filter(channels=kwargs['channel_id'])
        return self.list(request, *args, **kwargs)

    @action(detail=False)
    def choices(self, request, *args, **kwargs):
        queryset = Item.objects.filter(desk=request.desk)
        queryset = self.filter_queryset(queryset)
        queryset = queryset.values(
            'id', 'item_type_id', 'workflow_state_id', title=KeyTextTransform('title', 'json_content')
        )
        return Response(queryset)

    @action(detail=False, methods=['PUT'])
    def export(self, request, *args, **kwargs):
        AllItemsXLSExportJob.launch_r(self.request, timeout='30m')
        return Response(status=status.HTTP_202_ACCEPTED)

    @action(detail=True, url_path='diff/(?P<left_session_pk>\d+)/(?P<right_session_pk>\d+)',)
    def diff(self, request, pk, left_session_pk=None, right_session_pk=None):
        """
        Get a diff between 2 EditSessions.
        """
        self.base_queryset = Item.accessible_objects
        item = self.get_object()

        # Restrict access to private items
        if not user_can_access_item(request, item):
            raise PermissionDenied(_("Cet item est privé"))

        left = get_object_or_404(EditSession.objects, pk=left_session_pk, item=item)
        right = get_object_or_404(EditSession.objects, pk=right_session_pk, item=item)

        return Response(diff.item_content_diff_for_frontend(left, right))

    @action(detail=True, methods=['PUT'])
    def update_content(self, request, *args, **kwargs):
        """
        Fallback API to integrate live-edit changes when the websocket connection is not available.
        """
        item = self.get_object()
        changes = request.data.get('changes', [])
        update_result = ItemContentUpdater(request.user.id, item.id).apply_changes(changes)
        # Update the selection after propagating the change, and only if they were accepted
        if update_result['accepted']:
            broadcaster.broadcast_users_on_item(item.id)

        return Response({
            'desynchronized': len(update_result['rejected']) > 0,
            'accepted_changes': update_result['accepted'],
            'session': EditSessionLightSerializer(item.last_session).data
        })

    @action(detail=True, methods=['PATCH'])
    def update_workflow_state(self, request, *args, **kwargs):
        comment_content = request.data.pop('comment', None)
        self.activity_update_verb = Activity.VERB_UPDATED_WORKFLOW
        self.partial_update(request, *args, **kwargs)
        # Reload the item so we have an up-to-date workflow_state representation in the serializer
        item = self.get_object()
        if comment_content:
            create_comment_and_activity(
                instance=item,
                comment_content=comment_content,
                user=self.request.user
            )
        broadcaster.broadcast_item(item.id, self.request.user.id)
        return Response(self.get_serializer(item).data)

    @action(detail=True, methods=['PUT'])
    def put_in_trash(self, request, *args, **kwargs):
        """
        Change item visibility from 'visible' to 'trash'
        """
        item = self.get_object()
        self.action_trash(item)
        return Response(self.get_serializer(item).data)

    @action(detail=True, methods=['PUT'], base_queryset=Item.in_trash_objects)
    def restore_from_trash(self, request, *args, **kwargs):
        """
        Change item visibility from 'trash' to 'visible'
        """
        item = self.get_object()
        self.action_untrash(item)
        return Response(self.get_serializer(item).data)

    @action(detail=True, methods=['PUT'], base_queryset=Item.in_trash_objects)
    def soft_delete(self, request, *args, **kwargs):
        """
        Item soft delete consists in "hiding" the item, not deleting it from DB.
        Soft deleted items can be restored.
        """
        if request.user.permissions.is_restricted_editor:
            raise PermissionDenied()

        item = self.get_object()
        self.action_hide(item)
        return Response(self.get_serializer(item).data)

    @action(detail=True, methods=['PUT'])
    def create_major_version(self, request, *args, **kwargs):
        item = self.get_object()

        with transaction.atomic():
            item.create_major_version(self.request.user)
            self.create_activity(target=item, verb=Activity.VERB_CREATE_MAJOR_VERSION)

        broadcaster.broadcast_item(
            item_id=item.id,
            sender_id=self.request.user.id
        )
        return Response(EditSessionSerializer(item.last_session).data)

    @action(detail=True, methods=['PUT'])
    def restore_session(self, request, *args, **kwargs):
        item = self.get_object()
        session_id = self.request.data.get('session_id')
        session = get_object_or_404(
            EditSession,
            id=session_id,
            item=item
        )

        with transaction.atomic():
            item.restore_session(request.user, session)
            self.create_activity(
                verb=Activity.VERB_RESTORED,
                target=item,
                action_object=session
            )

        broadcaster.broadcast_item(
            item_id=item.id,
            restored_version=session.version,
            restored_by=PilotUserLightSerializer(request.user).data
        )

        return Response(self.get_serializer(item).data)

    # ===================
    # Actions
    # ===================

    def get_bulk_action_handlers(self):
        return {
            'trash': self.action_trash,
            'update': self.action_update,
            'copy': self.action_copy,
        }

    def action_trash(self, item, params={}):
        if not user_can_access_item(self.request, item):
            return

        item.updated_by = self.request.user
        item.in_trash = True
        item.save()
        self.create_activity(target=item, verb=Activity.VERB_PUT_IN_TRASH)
        HierarchyConsistencyJob.launch_for_item(self.request, item)

    def action_untrash(self, item, params={}):
        try:
            ItemUsageLimit(self.request.desk).check_limit()
        except UsageLimitReached as e:
            return Response(str(e), status=status.HTTP_403_FORBIDDEN)

        if not user_can_access_item(self.request, item):
            return

        item.updated_by = self.request.user
        item.in_trash = False
        item.save()
        self.create_activity(target=item, verb=Activity.VERB_RESTORED_FROM_TRASH)
        HierarchyConsistencyJob.launch_for_item(self.request, item)

    def action_hide(self, item, params={}):
        if not user_can_access_item(self.request, item):
            return

        with transaction.atomic():
            item.hide(user=self.request.user)
            for asset in item.assets.filter(in_media_library=False):
                asset.hide(user=self.request.user)
            self.create_activity(target=item, verb=Activity.VERB_HIDDEN)

        HierarchyConsistencyJob.launch_for_item(self.request, item)

    def action_update(self, item, params={}):
        if not user_can_access_item(self.request, item):
            return

        self.update_instance(instance=item, data=params, partial=True)

    def action_copy(self, item, params={}):
        if not user_can_access_item(self.request, item):
            return

        copy_item(item=item, created_by=self.request.user)

    # ===================
    # Helpers
    # ===================

    def filter_on_task_date(self, queryset, start=None, end=None, on=None):
        """
        Helper function that generate the filtering on dates depending on :
           * The state dates on which to apply the lookup (depends on self.is_calendar)
           * The start, end, on date
        """
        if on:
            # We have an exact date, so it will be an exact day lookup
            lookup_type = "exact"
            lookup_value = on

        if start and end:
            # We have a start and an end, so it will be a date range lookup
            lookup_type = "range"
            lookup_value = (start, end)
        elif start:
            # We have a start only, so it will be a greater than lookup
            lookup_type = "gte"
            lookup_value = start
        elif end:
            # We have a end only, so it will be a lesser than lookup
            lookup_type = "lte"
            lookup_value = end

        query = Q(**{'tasks__deadline__date__' + lookup_type: lookup_value})

        # Decide on which kind of task we should filter
        if self.is_calendar:
            # Any task
            return queryset.filter(query)
        else:
            # Publication task only
            return queryset.filter(query, tasks__is_publication=True)

    def limit_queryset_in_time(self, queryset):
        """
        Limit the queryset in time.
        Searches for `start`,`end`, `period`, `on` parameters in the query string.

        The `start`, `end` and `on` parameters must be '%Y-%m-%d' formatted:
            start: str, '%Y-%m-%d' formatted, e.g. 2013-11-10
            end: str, '%Y-%m-%d' formatted, e.g. 2013-11-10

        The `period` parameter must be an integer and must be in hours.

        If `start` and `end` are found, limits the queryset to items between start and end.
        If `on` is found, limits the queryset to items which happens on that day.
        If `period` is found, limits the queryset to now + timedelta(hours=period)
        If none of `start`, `end` or `on` are found, and `self.is_calendar` is True,
        will default to the current month
        """
        start = parse_date(self.request.query_params.get('start', ''))
        end = parse_date(self.request.query_params.get('end', ''))
        on = parse_date(self.request.query_params.get('on', ''))

        if start or end or on:
            return self.filter_on_task_date(queryset, start, end, on)
        elif self.is_calendar:
            # Fallback to the current month range when fallback_to_month is True
            # and start/end are not both specified
            today = datetime.date.today()
            start = today.replace(day=1)
            end = start + datetime.timedelta(days=31)
            return self.filter_on_task_date(queryset, start, end)

        try:
            period_in_hours = int(self.request.query_params.get('period', None))
        except (TypeError, ValueError):
            return queryset

        allowed_hours = [choice[0] for choice in SavedFilter.PERIOD_CHOICES if choice[0]]
        if period_in_hours and period_in_hours in allowed_hours:
            start = datetime.date.today()
            end = start + datetime.timedelta(hours=period_in_hours)
            return self.filter_on_task_date(queryset, start, end)

        return queryset


class SharedItemViewSet(api_utils.SharedApiMixin,
                        ItemViewSet):
    permission_classes = [
        AllowAny
    ]

    @action(detail=False, url_path='list')
    def shared_list(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(
        detail=False,
        is_calendar=True,
        pagination_class=None,
        url_path='calendar',
    )
    def shared_calendar(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class EditSessionList(generics.ListAPIView):
    """
    Get one full session with content when user want to display one specific version
    """
    permission_classes = [
        api_utils.DeskPermission
    ]
    serializer_class = EditSessionLightSerializer

    def get_queryset(self):
        item = get_object_or_404(
            Item.accessible_objects.filter_by_permissions(self.request.user),
            pk=self.kwargs['item_pk'],
            desk=self.request.desk
        )

        # Restrict access to private items
        if not user_can_access_item(self.request, item):
            raise PermissionDenied(_("Cet item est privé"))

        return item.sessions.all()


class EditSessionRetrieve(generics.RetrieveAPIView):
    """
    Get one full session with content when user want to display one specific version
    """
    permission_classes = [
        api_utils.DeskPermission
    ]
    queryset = EditSession.objects.all()
    serializer_class = EditSessionSerializer

    def check_object_permissions(self, request, session):
        """
        Restrict access to private items to allowed users only
        """
        super(EditSessionRetrieve, self).check_object_permissions(request, session)

        item = session.item
        # Restrict access to private items
        if not user_can_access_item(request, item):
            raise PermissionDenied(_("Cet item est privé"))

    def get_queryset(self):
        """
        Limit visible item sessions to the current desk
        and the item from the url
        """
        return (
            super(EditSessionRetrieve, self)
            .get_queryset()
            .filter(
                item_id=self.kwargs.get('item_pk'),
                item__desk=self.request.desk
            )
        )
