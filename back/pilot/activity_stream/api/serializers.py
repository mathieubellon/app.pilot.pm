import typing

from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from pilot.activity_stream.models import Activity
from pilot.pilot_users.api.serializers import PilotUserLightSerializer
from pilot.utils.api.generic import serialize_generic_linked_object

from pilot.utils.api.serializers import DocumentedSerializerMixin
from pilot.utils.diff import format_diff_for_api


class ActivitySerializer(DocumentedSerializerMixin, serializers.ModelSerializer):
    doc = {
        'action_object':
            "The [Generic linked object](#section/Core-concepts/Generic-linked-object-serialization) "
            "directly concerned by the verb, if different from the target",
        'actor_display':
            "The entity who performed the Activity. May be one of"
            "<ul>"
            "<li>the username of an internal PilotUser</li>"
            "<li>the email of an external user</li>"
            "<li>the source of an automatic Activity : pilot bot or public API</li>"
            "</ul>",
        'diff':
            "A [Diff array](#section/Core-concepts/Diff), "
            "when the Activity represents an update.<br />"
            "The updated object will generally be the target. "
            "Exception : for task updates ( verb=='task_updated' ), "
            "then the updated object will be the task in action_object. ",
        'is_comment':
            "Tells if this Activity represents a comment on the target. <br />"
            "If true, the comment object is available in the action_object field.",
        'target':
            "The [Generic linked object](#section/Core-concepts/Generic-linked-object-serialization) "
            "where the Activity took place",
        'verb_display':
            "A localized human-readable label for the verb",
    }

    action_object = serializers.SerializerMethodField()
    actor_display = serializers.ReadOnlyField(source="get_actor_display")
    diff = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()
    user = PilotUserLightSerializer(source='actor', read_only=True)
    verb_display = serializers.ReadOnlyField(source='get_verb_display')

    class Meta:
        model = Activity
        depth = 1
        fields = (
            'action_object',
            'actor_display',
            'created_at',
            'diff',
            'id',
            'is_comment',
            'target',
            'user',
            'verb',
            'verb_display',
        )

    def get_action_object(self, activity) -> dict:
        return serialize_generic_linked_object(
            content_type=activity.action_object_content_type,
            linked_object=activity.action_object,
            deleted_repr=activity.action_object_str
        )

    @swagger_serializer_method(serializer_or_field=serializers.ListField(serializers.DictField))
    def get_diff(self, activity) -> typing.List[dict]:
        # Special case for task diff : use the action_object instead of the target
        if activity.verb == Activity.VERB_TASK_UPDATED:
            content_type = activity.action_object_content_type
        else:
            content_type = activity.target_content_type

        return format_diff_for_api(
            diff=activity.diff,
            content_type=content_type
        )

    def get_target(self, activity) -> dict:
        return serialize_generic_linked_object(
            content_type=activity.target_content_type,
            linked_object=activity.target,
            deleted_repr=activity.target_str
        )
