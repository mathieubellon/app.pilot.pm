from rest_framework import serializers

from pilot.assets.api.serializers import AssetForSharingSerializer
from pilot.channels.api.light_serializers import ChannelUltraLightSerializer
from pilot.item_types.api.serializers import ItemTypeSerializer
from pilot.items.api.light_serializers import ItemLightSerializer, serialize_editor
from pilot.items.models import Item
from pilot.itemsfilters.api.serializers import SavedFilterSerializer
from pilot.pilot_users.api.serializers import PilotUserLightSerializer
from pilot.projects.api.light_serializers import ProjectLightSerializer
from pilot.sharings.api.serializers_base import BaseSharingSerializer
from pilot.sharings.models import Sharing, validate_sharing
from pilot.utils.api.serializers import SmartPrimaryKeyRelatedField


class SharingSerializer(BaseSharingSerializer):
    channel = ChannelUltraLightSerializer(read_only=True)
    channel_id = SmartPrimaryKeyRelatedField(required=False, allow_null=True)
    item = ItemLightSerializer(required=False, allow_null=True)
    item_id = SmartPrimaryKeyRelatedField(required=False, allow_null=True)
    project = ProjectLightSerializer(read_only=True)
    project_id = SmartPrimaryKeyRelatedField(required=False, allow_null=True)
    saved_filter = SavedFilterSerializer(read_only=True)
    saved_filter_id = SmartPrimaryKeyRelatedField(required=False, allow_null=False)

    class Meta:
        model = Sharing
        fields = (
            'channel',
            'channel_id',
            'created_at',
            'created_by',
            'deactivated',
            'email',
            'id',
            'is_editable',
            'item',
            'item_id',
            'feedbacks',
            'message',
            'password',
            'project',
            'project_id',
            'public_url',
            'query_string',
            'saved_filter',
            'saved_filter_id',
            'token',
            'type',
            'url',
        )

    def validate(self, attrs):
        # Create a Sharing object without saving it, just for the validation
        sharing = Sharing(**attrs)
        validate_sharing(sharing)
        return attrs


class SharedItemSerializer(serializers.ModelSerializer):
    annotations = serializers.JSONField(required=False, allow_null=True)
    assets = AssetForSharingSerializer(many=True)
    channels_names = serializers.SerializerMethodField()
    content = serializers.JSONField(required=False)
    frozen_by = PilotUserLightSerializer(read_only=True)
    item_type = ItemTypeSerializer()
    last_edition_datetime = serializers.ReadOnlyField()
    last_editor = serializers.SerializerMethodField()
    project = ProjectLightSerializer(read_only=True)
    publication_dt = serializers.ReadOnlyField()

    class Meta:
        model = Item
        fields = (
            'annotations',
            'assets',
            'channels_names',
            'content',
            'field_versions',
            'frozen',
            'frozen_at',
            'frozen_by',
            'frozen_message',
            'id',
            'item_type',
            'last_edition_datetime',
            'last_editor',
            'project',
            'publication_dt',
        )

    def get_channels_names(self, item):
        return [channel.name for channel in item.channels.all()]

    def get_last_editor(self, item):
        return serialize_editor(item.last_editor)
