from rest_framework import serializers

from pilot.itemsfilters.models import InternalSharedFilter, SavedFilter
from pilot.pilot_users.api.serializers import PilotUserLightSerializer
from pilot.sharings.api.serializers_base import LinkedSharingSerializer
from pilot.utils.api.serializers import SmartPrimaryKeyRelatedField


class SavedFilterSerializer(serializers.ModelSerializer):
    sharings = LinkedSharingSerializer(many=True, read_only=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')
    user = PilotUserLightSerializer(read_only=True)

    class Meta:
        model = SavedFilter
        fields = (
            'display_all_tasks',
            'display_tasks',
            'display_projects',
            'query',
            'id',
            'is_sliding_calendar',
            'sharings',
            'title',
            'type',
            'url',
            'user'
        )


class SavedFilterLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedFilter
        fields = (
            'id',
            'title',
        )


class InternalSharedFilterSerializer(serializers.ModelSerializer):
    saved_filter = SavedFilterLightSerializer(read_only=True)
    saved_filter_id = SmartPrimaryKeyRelatedField(required=True, allow_null=False)
    users = PilotUserLightSerializer(many=True, read_only=True)

    class Meta:
        model = InternalSharedFilter
        fields = (
            'id',
            'message',
            'saved_filter',
            'saved_filter_id',
            'users',
        )
