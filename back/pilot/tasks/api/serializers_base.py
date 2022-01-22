from rest_framework import serializers

from pilot.notifications.api.serializers import ReminderSerializer
from pilot.pilot_users.api.serializers import PilotUserLightSerializer
from pilot.tasks.models import Task
from pilot.utils import models as models_utils
from pilot.utils.api.serializers import SmartPrimaryKeyRelatedField, NaiveDateTimeField


class BaseTaskSerializer(serializers.ModelSerializer):
    serializers.ModelSerializer.serializer_field_mapping[models_utils.NaiveDateTimeField] = NaiveDateTimeField

    assignees = PilotUserLightSerializer(many=True, read_only=True)
    assignees_id = SmartPrimaryKeyRelatedField(source='assignees', many=True, required=False, allow_null=True)
    done_by = PilotUserLightSerializer(read_only=True)
    # !! WARNING : don't use this, see below !!
    # done_at = serializers.ReadOnlyField()
    reminders = ReminderSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = (
            'assignees',
            'assignees_id',
            'can_be_hidden',
            'deadline',
            'done',
            'done_at',
            'done_by',
            'id',
            'is_publication',
            'name',
            'order',
            'reminders',
            # 'show_in_publishing_calendar',
        )
        # There's an extremely weird bug with the done-at field.
        # When tasks are serialized within the nested serializer ItemSerializers.tasks
        # and we use `done_at = serializers.ReadOnlyField()`,
        # then the done_at field end up being a datetime object instead of an ISO string.
        # This bug does not triggers if we use read_only_fields as below, so we'll just stick with that.
        read_only_fields = (
            'done_at',
        )


class LinkedTaskSerializer(BaseTaskSerializer):
    pass


class TaskLightSerializer(BaseTaskSerializer):
    """
    Serializer with lighten data, aimed at returning a large number of items into the calendar API
    """

    class Meta:
        model = Task
        fields = (
            'deadline',
            'id',
            'is_publication',
            'name',
            # 'show_in_publishing_calendar',
        )
