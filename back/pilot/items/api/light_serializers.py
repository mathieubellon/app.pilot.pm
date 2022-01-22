from cacheout import lru_memoize
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from pilot.item_types.api.serializers import ItemTypeSerializer
from pilot.items.models import EditSession, Item
from pilot.pilot_users.models import PilotUser
from pilot.projects.api.light_serializers import ProjectLightSerializer
from pilot.pilot_users.api.serializers import PilotUserLightSerializer


@lru_memoize(maxsize=128)
def _serialize_user_editor(user_id):
    """
    An EditSession can have multiple editors, and each display of the ItemDetails page will
    call the /api/items/sessions API which fetch all the EditSessions of an Item.

    Moreover, most of the editors of a single Item will be the same, so we'll call multiple time this function
    with the same parameter.

    That's an ideal use case for a cache, which will avoid hitting to much the db.
    The in-memory cache may not be sufficient, in which case we'll need to use redis and cache the users there.
    """
    try:
        return PilotUserLightSerializer(instance=PilotUser.objects.get(id=user_id)).data
    except ObjectDoesNotExist:
        return '?'


def serialize_editor(editor):
    # A PilotUser id ( internal user )
    if isinstance(editor, int):
        return _serialize_user_editor(editor)
    # An email ( external user )
    else:
        return editor


class ItemLightSerializer(serializers.ModelSerializer):
    item_type = ItemTypeSerializer(read_only=True)
    project = ProjectLightSerializer(read_only=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Item
        fields = (
            'id',
            'item_type',
            'title',
            'project',
            'url',
        )


class ItemLinkedSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source='get_language_display')
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Item
        fields = (
            'id',
            'language',
            'title',
            'updated_at',
            'url',
        )


# Serialize a session without the (possibly heavy) content
class EditSessionLightSerializer(serializers.ModelSerializer):
    editors = serializers.SerializerMethodField()
    restored_from_version = serializers.CharField(source='restored_from.version', read_only=True)

    class Meta:
        model = EditSession
        fields = (
            'editors',
            'end',
            'id',
            'restored_from_version',
            'start',
            'version',
        )

    def get_editors(self, item):
        return [serialize_editor(editor) for editor in item.editors]
