from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.fields import empty

from pilot.assets.api.serializers import AssetLightSerializer
from pilot.channels.api.serializers import ChannelForItemDetailSerializer
from pilot.items.api.light_serializers import ItemLinkedSerializer, serialize_editor
from pilot.items.models import EditSession, Item
from pilot.labels.api.serializers import LabelLightSerializer
from pilot.pilot_users.models import DEFAULT_AVATAR
from pilot.projects.api.serializers import ProjectForItemDetailSerializer
from pilot.projects.api.light_serializers import ProjectLightSerializer
from pilot.channels.api.light_serializers import ChannelUltraLightSerializer
from pilot.item_types.item_content import init_item_content, ContentSchemaField
from pilot.pilot_users.api.serializers import PilotUserLightSerializer
from pilot.sharings.api.serializers_base import LinkedSharingSerializer
from pilot.targets.api.serializers import TargetSerializer, TargetUltraLightSerializer
from pilot.tasks.api.serializers_base import TaskLightSerializer, LinkedTaskSerializer
from pilot.tasks.models import TaskGroup
from pilot.workflow.api.serializers import WorkflowStateSerializer, WorkflowStateLightSerializer
from pilot.utils.api.serializers import Iso8601Field, SmartPrimaryKeyRelatedField, NaiveDateTimeField
from pilot.item_types.api.serializers import ItemTypeSerializer, ItemTypeLightSerializer
from pilot.utils.perms.private_items import user_can_access_item, user_has_private_item_perm


class SharableItemSerializerMixin(object):
    def __init__(self, *args, **kwargs):
        super(SharableItemSerializerMixin, self).__init__(*args, **kwargs)
        if 'context' in kwargs:
            # Serializers are passed a context dictionary, which contains the view instance.
            view = kwargs['context']['view']
            # Look for 'token' in view kwargs.
            self.token = view.kwargs.get('token')
            # If they exist replace the default `get_absolute_url` by `get_public_absolute_url`.
            if self.token:
                self.fields['url'] = serializers.SerializerMethodField('get_public_absolute_url')

    def get_public_absolute_url(self, item):
        # Allow an anonymous user to see the details of an Item.
        return reverse('ui_shared_item', kwargs={
            'item_pk': item.pk,
            'token': self.token,
        })


class ItemAccessMixin(serializers.Serializer):
    owners_string = serializers.SerializerMethodField()
    user_has_access = serializers.SerializerMethodField()
    user_has_private_perm = serializers.SerializerMethodField()

    def get_owners_string(self, item):
        return ", ".join([item.author] + [owner.get_short_name() for owner in item.owners.all()])

    def get_user_has_access(self, item):
        if 'view' not in self._context:
            return None

        request = self._context['view'].request
        return user_can_access_item(request, item)

    def get_user_has_private_perm(self, item):
        if 'view' not in self._context:
            return None

        request = self._context['view'].request
        return user_has_private_item_perm(request.user, item)


class AnnotationUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    # Don't use an URLField, it causes issues in testing, and PilotAvatarMixin send base64-encoded data in DEBUG
    avatar = serializers.CharField(required=False, allow_blank=True, allow_null=True, default=DEFAULT_AVATAR)


class AnnotationCommentSerializer(serializers.Serializer):
    date = Iso8601Field()
    content = serializers.JSONField(required=False, allow_null=True)
    user = AnnotationUserSerializer()


class AnnotationSerializer(serializers.Serializer):
    id = serializers.CharField()
    # Set required false because annotating an image won't produce any range
    range = serializers.DictField(required=False)
    # Set required false because annotating some text won't produce any shape
    shape = serializers.DictField(required=False, allow_null=True)
    mainComment = AnnotationCommentSerializer()
    comments = AnnotationCommentSerializer(many=True)
    resolved = serializers.BooleanField(default=False)
    resolvedBy = AnnotationUserSerializer(required=False, allow_null=True)
    # Do NOT trim whitespace on selectedText,
    # otherwise prosemirror js will see a difference in the text.
    # Set required false because annotating an image won't produce any selectedText
    selectedText = serializers.CharField(trim_whitespace=False, required=False, allow_blank=True, allow_null=True)


class EditSessionSerializer(serializers.ModelSerializer):
    annotations = serializers.JSONField(required=False, allow_null=True)
    # Technical values for the content
    content = serializers.JSONField(required=False)
    content_schema = ContentSchemaField(source='get_content_schema', required=False, read_only=True)
    editors = serializers.SerializerMethodField()
    restored_from_version = serializers.CharField(source='restored_from.version', read_only=True)

    class Meta:
        model = EditSession
        fields = (
            'annotations',
            'content',
            'content_schema',
            'editors',
            'end',
            'id',
            'restored_from_version',
            'start',
            'version'
        )

    def get_editors(self, item):
        return [serialize_editor(editor) for editor in item.editors]


class ItemListSerializer(SharableItemSerializerMixin, ItemAccessMixin, serializers.ModelSerializer):
    channels = ChannelUltraLightSerializer(many=True, read_only=True)
    has_owners = serializers.SerializerMethodField()
    # As an optimization, don't serialize the full item type, we'll retreive it into the frontend.
    item_type_id = serializers.PrimaryKeyRelatedField(read_only=True)
    language = serializers.ReadOnlyField()
    project = ProjectLightSerializer(read_only=True)
    publication_dt = serializers.ReadOnlyField()
    search_headline = serializers.ReadOnlyField()
    url = serializers.ReadOnlyField(source='get_absolute_url')
    workflow_state = WorkflowStateLightSerializer(read_only=True)

    class Meta:
        model = Item
        fields = (
            'channels',
            'has_owners',
            'id',
            'in_trash',
            'is_private',
            'item_type_id',
            'language',
            'project',
            'publication_dt',
            'search_headline',
            'title',
            'url',
            'user_has_access',
            'workflow_state'
        )

    def __init__(self, *args, **kwargs):
        super(ItemListSerializer, self).__init__(*args, **kwargs)
        # We should not see hidden projects
        for item in self.instance or []:
            if item and item.project and item.project.hidden:
                item.project = None

    def get_has_owners(self, item):
        # owners are prefetched, so the .all() won't hit the db
        return bool(item.owners.all())


class ItemCalendarSerializer(SharableItemSerializerMixin, serializers.ModelSerializer):
    """
    Serializer with lighten data, aimed at returning a large number of items into the calendar API
    """
    channels = ChannelUltraLightSerializer(many=True, read_only=True)
    item_type = ItemTypeLightSerializer(read_only=True)
    project = ProjectLightSerializer()
    targets = TargetUltraLightSerializer(many=True, read_only=True)
    tasks = TaskLightSerializer(many=True, required=False, read_only=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')
    workflow_state = WorkflowStateLightSerializer(read_only=True)

    class Meta:
        model = Item
        fields = (
            'channels',
            'id',
            'item_type',
            'language',
            'project',
            'targets',
            'tasks',
            'title',
            'url',
            'workflow_state'
        )

    def __init__(self, *args, **kwargs):
        super(ItemCalendarSerializer, self).__init__(*args, **kwargs)
        # We should not see hidden projects
        for item in self.instance or []:
            if item and item.project and item.project.hidden:
                item.project = None


class ItemInaccessibleSerializer(ItemAccessMixin, serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = (
            'id',
            'owners_string',
            'title',
            'user_has_access',
            'user_has_private_perm',
        )


class ItemSerializer(SharableItemSerializerMixin, ItemAccessMixin, serializers.ModelSerializer):
    annotations = serializers.JSONField(required=False, allow_null=True)
    assets = AssetLightSerializer(many=True, read_only=True)
    channels = ChannelForItemDetailSerializer(many=True, read_only=True)
    channels_id = SmartPrimaryKeyRelatedField(source='channels', many=True, required=False, allow_null=True)
    content = serializers.JSONField(required=False)
    created_by = PilotUserLightSerializer(read_only=True)
    creation_task_group_id = SmartPrimaryKeyRelatedField(
        queryset=TaskGroup.objects.all(),
        required=False,
        allow_null=True
    )
    frozen_by = PilotUserLightSerializer(read_only=True)
    item_type = ItemTypeSerializer(read_only=True)
    last_editor = serializers.SerializerMethodField()
    master_translation = ItemLinkedSerializer(read_only=True)
    owners = PilotUserLightSerializer(many=True, read_only=True)
    owners_id = SmartPrimaryKeyRelatedField(source='owners', many=True, required=False, allow_null=True)
    project = ProjectForItemDetailSerializer(read_only=True)
    project_id = SmartPrimaryKeyRelatedField(required=False, allow_null=True)
    publication_dt = NaiveDateTimeField(required=False, allow_null=True)
    sharings = LinkedSharingSerializer(many=True, read_only=True)
    tags = LabelLightSerializer(many=True, read_only=True)
    tags_id = SmartPrimaryKeyRelatedField(source='tags', many=True, required=False, allow_null=True)
    targets = TargetSerializer(many=True, read_only=True)
    targets_id = SmartPrimaryKeyRelatedField(source='targets', many=True, required=False, allow_null=True)
    tasks = LinkedTaskSerializer(many=True, required=False, read_only=True)
    translation_siblings = serializers.SerializerMethodField()
    translations = ItemLinkedSerializer(many=True, read_only=True)
    translations_id = SmartPrimaryKeyRelatedField(source='translations', many=True, required=False, allow_null=True,
                                                  use_id_for_internal_value=False)
    updated_by = PilotUserLightSerializer(read_only=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')
    # Version property has been added by ItemQuerySet.annotate_version()
    version = serializers.ReadOnlyField()
    workflow_state = WorkflowStateSerializer(read_only=True)
    workflow_state_id = SmartPrimaryKeyRelatedField(required=False, allow_null=True)

    class Meta:
        model = Item
        fields = (
            'annotations',
            'assets',
            'channels',
            'channels_id',
            'content',
            'created_at',
            'created_by',
            'creation_task_group_id',
            'field_versions',
            'frozen',
            'frozen_at',
            'frozen_by',
            'frozen_message',
            'id',
            'in_trash',
            'is_private',
            'item_type',
            'language',
            'last_edition_datetime',
            'last_editor',
            'master_translation',
            'owners',
            'owners_id',
            'owners_string',
            'project',
            'project_id',
            'publication_dt',
            'sharings',
            'tags',
            'tags_id',
            'targets',
            'targets_id',
            'tasks',
            'title',
            'translations',
            'translations_id',
            'translation_siblings',
            'updated_at',
            'updated_by',
            'url',
            'user_has_access',
            'user_has_private_perm',
            'version',
            'workflow_state',
            'workflow_state_id',
        )
        read_only_fields = (
            'last_edition_datetime',
            'created_at',
            'updated_at'
        )

    default_error_messages = {
        'not_a_dict': _('Expected a dictionary of items but got type "{input_type}".')
    }

    def __init__(self, *args, **kwargs):
        item_type = kwargs.pop('item_type', None)

        super(ItemSerializer, self).__init__(*args, **kwargs)

        # Serializers are passed a context dictionary, which contains the view instance.
        user = None
        if 'context' in kwargs:
            view = kwargs['context']['view']
            user = view.request.user
        item = self.instance

        if item:
            # Users that do not have private access cannot modify the is_private property
            if user and not user_has_private_item_perm(user, item):
                self.fields['is_private'].read_only = True

            # We should not see hidden projects
            if item.project and item.project.hidden:
                item.project = None

        self.item_type = None
        if item_type:
            self.item_type = item_type
        elif item:
            self.item_type = item.item_type

    def get_last_editor(self, item):
        return serialize_editor(item.last_editor)

    def get_translation_siblings(self, item):
        # TODO: move this to the api_prefetch() when the POC is validated
        if not item.master_translation:
            return []
        siblings = Item.objects.filter(master_translation=item.master_translation)
        return ItemLinkedSerializer(siblings, many=True).data

    def validate_annotations(self, annotations_by_fields):
        if annotations_by_fields:
            if not isinstance(annotations_by_fields, dict):
                self.fail('not_a_dict', input_type=type(annotations_by_fields).__name__)

            # Validate annotations structure
            for field_name, annotations in annotations_by_fields.items():
                if not annotations:
                    continue

                for annotation_id, annotation in annotations.items():
                    AnnotationSerializer(data=annotation).is_valid(raise_exception=True)

        return annotations_by_fields

    def save_item(self, item, validated_data):
        # Remove m2m data to prevent nested writes errors.
        assets = validated_data.pop('assets', empty)
        channels = validated_data.pop('channels', empty)
        owners = validated_data.pop('owners', empty)
        targets = validated_data.pop('targets', empty)
        tags = validated_data.pop('tags', empty)
        translations = validated_data.pop('translations', empty)

        for attr, value in validated_data.items():
            setattr(item, attr, value)

        item.save()

        # Set M2M fields
        # When None is used, set an empty M2M with an empty list
        if assets is not empty:
            item.assets.set(assets or [])
        if channels is not empty:
            item.channels.set(channels or [])
        if owners is not empty:
            item.owners.set(owners or [])
        if targets is not empty:
            item.targets.set(targets or [])
        if tags is not empty:
            item.tags.set(tags or [])
        if translations is not empty:
            # Prevent adding ourselves as both master and child translation
            translations = [translation for translation in (translations or [])
                            if translation.id != item.id]
            item.translations.set(translations)

        return item

    def create(self, validated_data):
        if not self.item_type:
            raise Exception("An item_type is needed to create an Item")

        # Set item type first so the content can be serialized
        item = Item(item_type=self.item_type)
        # Init the content with initial data defined in the schema.
        # Always init a content, even if the user did not sent one
        init_item_content(
            content=validated_data.setdefault('content', {}),
            content_schema=self.item_type.content_schema,
            creation=True
        )
        return self.save_item(item, validated_data)

    def update(self, item, validated_data):
        return self.save_item(item, validated_data)
