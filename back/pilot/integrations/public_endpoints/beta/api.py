from rest_flex_fields.filter_backends import FlexFieldsFilterBackend

from rest_framework import viewsets, mixins
from rest_framework.decorators import action

from pilot.channels.models import Channel
from pilot.item_types.models import ItemType
from pilot.items.models import Item
from pilot.projects.models import Project
from pilot.utils.api import PilotPageNumberPagination

from pilot.integrations import authentication
from pilot.integrations import throttling
from pilot.integrations.public_endpoints.beta import filters, serializers
from pilot.utils.projel.hierarchy import get_items_paths
from pilot.workflow.models import WorkflowState


class IntegrationsPagination(PilotPageNumberPagination):
    page_size = 10
    max_page_size = 100
    page_size_query_param = 'page_size'


class IntegrationsBaseViewSet(mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    authentication_classes = [authentication.ApiTokenAuthentication]
    permission_classes = [authentication.HasApiToken]
    throttle_classes = [
        throttling.TokenMinuteRateThrottle,
        throttling.TokenHourRateThrottle
    ]
    filter_backends = viewsets.ModelViewSet.filter_backends + [
        FlexFieldsFilterBackend,
    ]
    auto_remove_fields_from_query = False
    pagination_class = IntegrationsPagination
    default_ordering = '-updated_at'

    def get_queryset(self):
        return super(IntegrationsBaseViewSet, self).get_queryset().filter(desk=self.request.desk)


# ===================
# Channels endpoint
# ===================


class IntegrationsChannelViewSet(IntegrationsBaseViewSet):
    filter_class = filters.ChannelFilter
    serializer_class = serializers.IntegrationsChannelSerializer

    def get_queryset(self):
        return (
            Channel.objects
            .filter(desk=self.request.desk)
            .filter_by_permissions(self.request.user)
            .prefetch_related('owners')
            .order_by(self.default_ordering)
        )

    @action(detail=True, methods=['GET'])
    def items(self, request, *args, **kwargs):
        channel = self.get_object()
        items_paths = get_items_paths(channel.hierarchy)
        return IntegrationsItemInChannelViewSet.as_view({'get': 'list'}, items_paths=items_paths)(request._request)


# ===================
# Projects endpoint
# ===================


class IntegrationsProjectViewSet(IntegrationsBaseViewSet):
    filter_class = filters.ProjectFilter
    serializer_class = serializers.IntegrationsProjectSerializer

    def get_queryset(self):
        return (
            Project.objects
            .filter(desk=self.request.desk)
            .filter_by_permissions(self.request.user)
            .prefetch_related('channels', 'members', 'owners', 'tags', 'targets')
            .order_by(self.default_ordering)
        )


# ===================
# Items endpoint
# ===================


class IntegrationsItemViewSet(IntegrationsBaseViewSet):
    filter_class = filters.ItemFilter
    serializer_class = serializers.IntegrationsItemSerializer

    def get_queryset(self):
        return (
            Item.objects
            .filter(desk=self.request.desk)
            .filter_by_permissions(self.request.user)
            .with_content()
            .annotate_version()
            .select_related('item_type')
            .prefetch_related('channels', 'owners',  'tags', 'targets', 'tasks', 'translations')
            .order_by(self.default_ordering)
        )


class IntegrationsItemInChannelViewSet(IntegrationsItemViewSet):
    """
    This is a special viewset that will only be called from IntegrationsChannelViewSet.items()
    with the route channels/{channel_id}/items
    """
    serializer_class = serializers.IntegrationsItemInChannelSerializer
    # This attribute is a dict {item_id: path}
    # It is passed down by IntegrationsChannelViewSet.items()
    # and used by IntegrationsItemInChannelSerializer.get_path()
    items_paths = {}

# ===================
# Item Type endpoint
# ===================


class IntegrationsItemTypeViewSet(IntegrationsBaseViewSet):
    serializer_class = serializers.IntegrationsItemTypeSerializer
    queryset = ItemType.objects


# ===================
# Workflow State endpoint
# ===================


class IntegrationsWorkflowStateViewSet(IntegrationsBaseViewSet):
    serializer_class = serializers.IntegrationsWorkflowStateSerializer
    queryset = WorkflowState.objects
