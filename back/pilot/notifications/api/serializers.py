from rest_framework import serializers

from pilot.itemsfilters.api.serializers import SavedFilterLightSerializer
from pilot.notifications.models import Notification, NotificationFeed, Reminder
from pilot.pilot_users.api.serializers import PilotUserLightSerializer
from pilot.utils.api.serializers import SmartPrimaryKeyRelatedField, DocumentedSerializerMixin
from pilot.utils.api.generic import serialize_generic_linked_object
from pilot.utils.diff import format_diff_for_api


class NotificationFeedSerializer(serializers.ModelSerializer):
    saved_filter = SavedFilterLightSerializer(read_only=True)
    saved_filter_id = SmartPrimaryKeyRelatedField(required=False, allow_null=True)

    class Meta:
        model = NotificationFeed
        fields = (
            # 'activity_actor',
            # 'activity_content_type',
            # 'activity_object_id',
            # 'activity_verb',
            'feed_type',
            'id',
            'saved_filter',
            'saved_filter_id',
            'display_in_app',
            'send_email',
        )


class NotificationSerializer(DocumentedSerializerMixin, serializers.ModelSerializer):
    doc = {
        'content':
            "Textual message of the notification, in plain text.",
        'data':
            "Arbitrary additional data set by the creator of the Notification.",
        'linked_object':
            "The [Generic linked object](#section/Core-concepts/Generic-linked-object-serialization) "
            "concerned by the Notification. "
            "Warning : this may be null ( example : a data export has no linked object )",
        'source_feed':
            "Only if this Notification feed has been created by a NotificationFeed",
        'url':
            "This field hold the target url."
            "May be null if the target url is null.",
    }

    data = serializers.SerializerMethodField()
    linked_object = serializers.SerializerMethodField()
    send_by = PilotUserLightSerializer(read_only=True)
    source_feed = NotificationFeedSerializer(read_only=True)
    url = serializers.ReadOnlyField(source='get_target_url')

    class Meta:
        model = Notification
        fields = (
            'content',
            'data',
            'id',
            'is_read',
            'linked_object',
            'source_feed',
            'send_by',
            'send_at',
            'type',
            'url',
        )
        read_only_fields = (
            'content',
            'id',
            'send_at',
            'type',
        )

    def get_data(self, notification):
        data = notification.data

        diff = data.get('diff')
        if diff:
            data['diff'] = format_diff_for_api(
                diff=diff,
                content_type=notification.linked_object_content_type
            )

        return data

    def get_linked_object(self, notification):
        return serialize_generic_linked_object(
            content_type=notification.linked_object_content_type,
            linked_object=notification.linked_object
        )


class ReminderSerializer(serializers.ModelSerializer):
    target_type = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = Reminder
        fields = (
            'delta_unit',
            'delta_value',
            'id',
            'is_notification_sent',
            'target_type',
        )
