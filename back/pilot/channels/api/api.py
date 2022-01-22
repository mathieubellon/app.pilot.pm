from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_202_ACCEPTED

from pilot.channels.api.filters import ChannelFilter
from pilot.channels.api.serializers import ChannelChoiceSerializer, ChannelListSerializer, ChannelSerializer
from pilot.utils.projel.api import ProjelViewSet
from pilot.channels.models import Channel
from pilot.utils.projel.hierarchy import HierarchyConsistencyJob


class ChannelViewSet(ProjelViewSet):
    serializer_class = ChannelSerializer
    base_queryset = Channel.objects
    filter_class = ChannelFilter
    default_ordering = 'name'

    # ===================
    # Create / Update
    # ===================

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    # ===================
    # Custom routes
    # ===================

    @action(
        detail=False,
        base_queryset=Channel.active_objects,
        serializer_class=ChannelListSerializer
    )
    def active(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(
        detail=False,
        base_queryset=Channel.closed_objects,
        serializer_class=ChannelListSerializer
    )
    def closed(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(
        detail=False,
        base_queryset=Channel.active_objects,
        serializer_class=ChannelChoiceSerializer,
        pagination_class=None,
        default_ordering='name'  # On choices, order by 'name' by default
    )
    def choices(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(detail=True, methods=['PUT'])
    def remove_items(self,  request, *args, **kwargs):
        channel = self.get_object()
        item_ids = request.data.get('itemIds')
        channel.items.remove(*item_ids)
        HierarchyConsistencyJob.launch_r(self.request, channel)
        return Response(status=HTTP_202_ACCEPTED)
