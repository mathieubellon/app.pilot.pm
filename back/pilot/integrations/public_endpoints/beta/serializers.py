from rest_framework import serializers

from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.exceptions import ValidationError

from pilot.channels.models import Channel
from pilot.item_types.models import ItemType
from pilot.items.api.light_serializers import serialize_editor
from pilot.items.models import Item
from pilot.labels.models import Label
from pilot.pilot_users.models import PilotUser
from pilot.projects.models import Project
from pilot.targets.models import Target
from pilot.utils.api.serializers import SmartPrimaryKeyRelatedField, NaiveDateTimeField

from pilot.utils.prosemirror.prosemirror import prosemirror_json_to_html
from pilot.utils.serialization import SerializationFormat, get_dialect
from pilot.workflow.models import WorkflowState


class DescriptionMixin(FlexFieldsModelSerializer):
    description = serializers.SerializerMethodField()

    def get_description(self, projel):
        try:
            format_description = self._context['request'].query_params.get('format_description')
        except:
            format_description = None

        if not format_description or format_description == SerializationFormat.RAW:
            return projel.description

        try:
            dialect = get_dialect(format_description)
            return dialect.pm_converter(projel.description)
        except ValueError as e:
            raise ValidationError(e)


class IntegrationsUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = PilotUser
        fields = (
            'id',
            'username',
        )


class IntegrationsLabelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Label
        fields = (
            'color',
            'id',
            'name',
        )


class IntegrationsTargetSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()

    class Meta:
        model = Target
        fields = (
            'id',
            'description',
            'name',
        )

    def get_description(self, target):
        return prosemirror_json_to_html(target.description)


class IntegrationsChannelSerializer(DescriptionMixin, FlexFieldsModelSerializer):
    owners = SmartPrimaryKeyRelatedField(many=True, read_only=True)
    type = SmartPrimaryKeyRelatedField(read_only=True)
    updated_by = IntegrationsUserSerializer()

    class Meta:
        model = Channel
        fields = (
            'created_at',
            'created_by',
            'description',
            'hierarchy',
            'id',
            'name',
            'owners',
            'state',
            'type',
            'updated_at',
            'updated_by',
        )

    expandable_fields = {
        'created_by': (IntegrationsUserSerializer, {'source': 'created_by'}),
        'owners': (IntegrationsUserSerializer, {'source': 'owners', 'many': True}),
        'type': (IntegrationsLabelSerializer, {'source': 'type'}),
        'updated_by': (IntegrationsUserSerializer, {'source': 'updated_by'}),
    }


class IntegrationsItemTypeSerializer(serializers.ModelSerializer):
    """
    Serializer with lighten data, aimed at returning a large number of items by public API
    """
    class Meta:
        model = ItemType
        fields = (
            'content_schema',
            'id',
            'name',
        )


class IntegrationsWorkflowStateSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkflowState
        fields = (
            'color',
            'id',
            'label',
            'order',
        )


class IntegrationsProjectSerializer(DescriptionMixin, FlexFieldsModelSerializer):
    channels = SmartPrimaryKeyRelatedField(many=True, read_only=True)
    category = SmartPrimaryKeyRelatedField(read_only=True)
    members = SmartPrimaryKeyRelatedField(many=True, read_only=True)
    owners = SmartPrimaryKeyRelatedField(many=True, read_only=True)
    priority = SmartPrimaryKeyRelatedField(read_only=True)
    tags = SmartPrimaryKeyRelatedField(many=True, read_only=True)
    targets = SmartPrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Project
        fields = (
            'category',
            'channels',
            'created_at',
            'created_by',
            'description',
            'end',
            'hierarchy',
            'id',
            'name',
            'members',
            'owners',
            'priority',
            'start',
            'state',
            'tags',
            'targets',
            'updated_at',
            'updated_by',
        )

    expandable_fields = {
        'category': (IntegrationsLabelSerializer, {'source': 'category'}),
        'channels': (IntegrationsChannelSerializer, {'source': 'channels', 'many': True}),
        'created_by': (IntegrationsUserSerializer, {'source': 'created_by'}),
        'members': (IntegrationsUserSerializer, {'source': 'members', 'many': True}),
        'owners': (IntegrationsUserSerializer, {'source': 'owners', 'many': True}),
        'priority': (IntegrationsLabelSerializer, {'source': 'priority'}),
        'tags': (IntegrationsLabelSerializer, {'source': 'tags', 'many': True}),
        'targets': (IntegrationsTargetSerializer, {'source': 'targets', 'many': True}),
        'updated_by': (IntegrationsUserSerializer, {'source': 'updated_by'}),
    }


class IntegrationsItemLinkedSerializer(serializers.ModelSerializer):
    language = serializers.CharField(source='get_language_display')

    class Meta:
        model = Item
        fields = (
            'id',
            'language',
            'title',
            'updated_at',
        )


# https://github.com/rsinger86/drf-flex-fields#from-url-parameters
class IntegrationsItemSerializer(FlexFieldsModelSerializer):
    content = serializers.SerializerMethodField()
    channels = SmartPrimaryKeyRelatedField(many=True, read_only=True)
    item_type = SmartPrimaryKeyRelatedField(read_only=True)
    last_editor = serializers.SerializerMethodField()
    master_translation = SmartPrimaryKeyRelatedField(read_only=True)
    owners = SmartPrimaryKeyRelatedField(many=True, read_only=True)
    project = SmartPrimaryKeyRelatedField(read_only=True)
    publication_dt = NaiveDateTimeField(required=False, allow_null=True)
    tags = SmartPrimaryKeyRelatedField(many=True, read_only=True)
    targets = SmartPrimaryKeyRelatedField(many=True, read_only=True)
    translations = SmartPrimaryKeyRelatedField(many=True, read_only=True)
    # Version property has been added by ItemQuerySet.annotate_version()
    version = serializers.ReadOnlyField()
    workflow_state = SmartPrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Item
        fields = (
            'channels',
            'content',
            'created_at',
            'created_by',
            'id',
            'item_type',
            'language',
            'last_edition_datetime',
            'last_editor',
            'master_translation',
            'owners',
            'project',
            'publication_dt',
            'tags',
            'targets',
            'title',
            'translations',
            'updated_at',
            'updated_by',
            'version',
            'workflow_state',
        )
    expandable_fields = {
        'channels': (IntegrationsChannelSerializer, {'source': 'channels', 'many': True}),
        'created_by': (IntegrationsUserSerializer, {'source': 'created_by'}),
        'item_type': (IntegrationsItemTypeSerializer, {'source': 'item_type'}),
        'project': (IntegrationsProjectSerializer, {'source': 'project'}),
        'tags': (IntegrationsLabelSerializer, {'source': 'tags', 'many': True}),
        'targets': (IntegrationsTargetSerializer, {'source': 'targets', 'many': True}),
        'translations': ('pilot.integrations.endpoints.IntegrationsItemSerializer', {'source': 'translations', 'many': True}),
        'updated_by': (IntegrationsUserSerializer, {'source': 'updated_by'}),
        'workflow_state': (IntegrationsWorkflowStateSerializer, {'source': 'workflow_state'}),
    }

    def get_content(self, item):
        try:
            format_content = self._context['request'].query_params.get('format_content')
        except:
            format_content = None

        try:
            return item.serialize(format_content)
        except ValueError as e:
            raise ValidationError(e)

    def get_last_editor(self, item):
        return serialize_editor(item.last_editor)


class IntegrationsItemInChannelSerializer(IntegrationsItemSerializer):
    """
    This is a special serializer that will only be called from IntegrationsChannelViewSet.items()
    with the route channels/{channel_id}/items
    """
    path = serializers.SerializerMethodField()

    def get_path(self, item):
        view = self._context['view']
        return view.items_paths.get(item.id, [])

    class Meta:
        model = Item
        fields = sorted(IntegrationsItemSerializer.Meta.fields + (
            'path',
        ))
