from rest_framework import serializers

from pilot.item_types.item_content import ContentSchemaField
from pilot.item_types.models import ItemType
from pilot.utils.api.serializers import SmartPrimaryKeyRelatedField


class ItemTypeLightSerializer(serializers.ModelSerializer):
    """
    Serializer with lighten data, aimed at returning a large number of items into the calendar API
    """
    class Meta:
        model = ItemType
        fields = (
            'name',
        )


class ItemTypeSerializer(serializers.ModelSerializer):
    content_schema = ContentSchemaField(required=False)
    # An aggregated field provided by ItemTypeViewSet.get_queryset()
    linked_item_count = serializers.ReadOnlyField()
    metadata_schema = serializers.ReadOnlyField()
    task_group_id = SmartPrimaryKeyRelatedField(required=False, allow_null=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = ItemType
        fields = (
            'content_schema',
            'description',
            'icon_name',
            'id',
            'linked_item_count',
            'metadata_schema',
            'name',
            'task_group_id',
            'url'
        )
