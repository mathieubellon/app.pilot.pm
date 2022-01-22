"""
All serializers declared here are prefixed by "GLO" ( stand for "GenericLinkedObject" )
to distinguish them from the usual serializers
"""
from rest_framework import serializers

from pilot.assets.models import Asset, AssetRight
from pilot.channels.models import Channel
from pilot.comments.api.serializers import CommentSerializer
from pilot.comments.models import Comment
from pilot.items.models import EditSession, Item
from pilot.itemsfilters.api.serializers import InternalSharedFilterSerializer
from pilot.itemsfilters.models import InternalSharedFilter, SavedFilter
from pilot.labels.api.serializers import LabelLightSerializer
from pilot.pilot_users.api.serializers import PilotUserLightSerializer
from pilot.projects.models import Project
from pilot.sharings.models import ItemFeedback, Sharing
from pilot.tasks.models import Task
from pilot.wiki.models import WikiPage

STATE_ACTIVE = 'active'
STATE_HIDDEN = 'soft_deleted'
STATE_DELETED = 'terminated'


class GLOAssetSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Asset
        fields = (
            'id',
            'title',
            'url',
        )


class GLOAssetRightSerializer(serializers.ModelSerializer):
    asset = GLOAssetSerializer(read_only=True)
    medium = LabelLightSerializer(read_only=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = AssetRight
        fields = (
            'asset',
            'expiry',
            'id',
            'medium',
            'url',
        )


class GLOChannelSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Channel
        fields = (
            'id',
            'name',
            'url',
        )

class GLOProjectSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Project
        fields = (
            'id',
            'name',
            'url',
        )


class GLOItemSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Item
        fields = (
            'id',
            'title',
            'url',
        )


class GLOEditSessionSerializer(serializers.ModelSerializer):
    item = GLOItemSerializer(read_only=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = EditSession
        fields = (
            'id',
            'item',
            'url',
            'version',
        )


class GLOTaskSerializer(serializers.ModelSerializer):
    assignees = PilotUserLightSerializer(many=True, read_only=True)
    done_by = PilotUserLightSerializer(read_only=True)
    item = GLOItemSerializer(read_only=True)
    project = GLOProjectSerializer(read_only=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Task
        fields = (
            'assignees',
            'can_be_hidden',
            'deadline',
            'done',
            'done_at',
            'done_by',
            'id',
            'is_publication',
            'item',
            'name',
            'project',
            # 'show_in_publishing_calendar',
            'url',
        )


class GLOSavedFilterSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = SavedFilter
        fields = (
            'id',
            'title',
            'type',
            'url',
        )


class GLOSharingSerializer(serializers.ModelSerializer):
    channel = GLOChannelSerializer(read_only=True)
    project = GLOProjectSerializer(read_only=True)
    item = GLOItemSerializer(read_only=True)
    saved_filter = GLOSavedFilterSerializer(read_only=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Sharing
        fields = (
            'channel',
            'email',
            'item',
            'message',
            'project',
            'saved_filter',
            'token',
            'type',
            'url',
        )


class GLOItemFeedbackSerializer(serializers.ModelSerializer):
    item = GLOItemSerializer(read_only=True)
    sharing = GLOSharingSerializer(read_only=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = ItemFeedback
        fields = (
            'item',
            'feedback_message',
            'sharing',
            'status',
            'url',
        )


class GLOWikiPageSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = WikiPage
        fields = (
            'id',
            'name',
            'url',
        )


GLOInternalSharedFilterSerializer = InternalSharedFilterSerializer
GLOCommentSerializer = CommentSerializer


GLO_SERIALIZERS = {
    Asset: GLOAssetSerializer,
    AssetRight: GLOAssetRightSerializer,
    Channel: GLOChannelSerializer,
    Comment: GLOCommentSerializer,
    EditSession: GLOEditSessionSerializer,
    Item: GLOItemSerializer,
    ItemFeedback: GLOItemFeedbackSerializer,
    InternalSharedFilter: GLOInternalSharedFilterSerializer,
    SavedFilter: GLOSavedFilterSerializer,
    Project: GLOProjectSerializer,
    Sharing: GLOSharingSerializer,
    Task: GLOTaskSerializer,
    WikiPage: GLOWikiPageSerializer,
}


def serialize_generic_linked_object(content_type, linked_object, deleted_repr=None):
    if not content_type:
        return None

    model = content_type.model_class()

    if linked_object and not isinstance(linked_object, model):
        raise ValueError(f"linked_object {linked_object} is not of ContentType {content_type}")

    details = None
    if linked_object:
        linked_object_serializer = GLO_SERIALIZERS.get(model)
        if linked_object_serializer:
            details = linked_object_serializer(linked_object).data
        hidden = getattr(linked_object, 'hidden', False)
        state = STATE_HIDDEN if hidden else STATE_ACTIVE

    else:
        state = STATE_DELETED
        details = {
            'repr': deleted_repr
        }

    return {
        'content_type_id': content_type.id,
        'details': details,
        'model_name': model.__name__,
        'state': state,
    }
