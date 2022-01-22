from rest_framework import serializers

from pilot.items.api.light_serializers import ItemLightSerializer
from pilot.pilot_users.api.serializers import PilotUserLightSerializer
from pilot.sharings.models import ItemFeedback, Sharing
from pilot.utils.url import get_fully_qualified_url

from pilot.utils.api.serializers import SmartPrimaryKeyRelatedField


class ItemFeedbackSerializer(serializers.ModelSerializer):
    item = ItemLightSerializer(read_only=True)
    item_id = SmartPrimaryKeyRelatedField(required=True, allow_null=False)

    class Meta:
        model = ItemFeedback
        fields = (
            'created_at',
            'id',
            'item',
            'item_id',
            'feedback_message',
            'status'
        )


class BaseSharingSerializer(serializers.ModelSerializer):
    created_by = PilotUserLightSerializer(read_only=True)
    feedbacks = ItemFeedbackSerializer(many=True, read_only=True)
    # No need to set (write_only=True) on the password :
    # Authenticated users can display the password.
    # Public users must give the password to reach the serialized sharing,
    # so they already know it.
    password = serializers.CharField(required=False, write_only=False, allow_blank=True)
    query_string = serializers.ReadOnlyField(source='get_query_string')
    token = serializers.ReadOnlyField()
    url = serializers.ReadOnlyField(source='get_absolute_url')
    public_url = serializers.SerializerMethodField()

    class Meta:
        model = Sharing
        fields = (
            'created_at',
            'created_by',
            'email',
            'is_editable',
            'feedbacks',
            'message',
            'password',
            'public_url',
            'query_string',
            'token',
            'type',
            'url',
        )

    def get_public_url(self, sharing):
        return get_fully_qualified_url(sharing.get_public_absolute_url())


class LinkedSharingSerializer(BaseSharingSerializer):
    pass
