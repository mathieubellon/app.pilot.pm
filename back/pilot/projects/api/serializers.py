from rest_framework import serializers
from rest_framework.fields import empty

from pilot.assets.api.serializers import AssetLightSerializer
from pilot.labels.api.serializers import LabelLightSerializer
from pilot.pilot_users.api.serializers import PilotUserLightSerializer
from pilot.channels.api.light_serializers import ChannelLightSerializer
from pilot.projects.api.light_serializers import ProjectLightSerializer
from pilot.projects.models import Project
from pilot.sharings.api.serializers_base import LinkedSharingSerializer
from pilot.targets.api.serializers import TargetSerializer
from pilot.items.api.light_serializers import ItemLinkedSerializer
from pilot.tasks.api.serializers_base import LinkedTaskSerializer
from pilot.utils.api.serializers import SmartPrimaryKeyRelatedField


class ProjectForItemDetailSerializer(ProjectLightSerializer):
    """
    Serializer with data for the ItemDetail view
    """
    items = ItemLinkedSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = (
            'description',
            'hierarchy',
            'id',
            'items',
            'name',
            'url',
        )


class ProjectSerializer(serializers.ModelSerializer):
    assets = AssetLightSerializer(many=True, read_only=True)
    channels = ChannelLightSerializer(many=True, read_only=True)
    channels_id = SmartPrimaryKeyRelatedField(source='channels', many=True, required=False, allow_null=True)
    category = LabelLightSerializer(read_only=True)
    category_id = SmartPrimaryKeyRelatedField(required=False, allow_null=True)
    created_by = PilotUserLightSerializer(read_only=True)
    # items_count is annotated by ProjelQuerySet.detail_api_prefetch
    items_count = serializers.ReadOnlyField()
    members = PilotUserLightSerializer(many=True, read_only=True)
    members_id = SmartPrimaryKeyRelatedField(source='members', many=True, required=False, allow_null=True)
    owners = PilotUserLightSerializer(many=True, read_only=True)
    owners_id = SmartPrimaryKeyRelatedField(source='owners', many=True, required=False, allow_null=True)
    priority = LabelLightSerializer(read_only=True)
    priority_id = SmartPrimaryKeyRelatedField(required=False, allow_null=True)
    progress = serializers.ReadOnlyField(source='get_progress')
    sharings = LinkedSharingSerializer(many=True, read_only=True)
    tags = LabelLightSerializer(many=True, read_only=True)
    tags_id = SmartPrimaryKeyRelatedField(source='tags', many=True, required=False, allow_null=True)
    targets = TargetSerializer(many=True, read_only=True)
    targets_id = SmartPrimaryKeyRelatedField(source='targets', many=True, required=False, allow_null=True)
    tasks = LinkedTaskSerializer(many=True, required=False, read_only=True)
    updated_by = PilotUserLightSerializer(read_only=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Project
        fields = (
            'assets',
            'channels',
            'channels_id',
            'category',
            'category_id',
            'created_at',
            'created_by',
            'created_by_external_email',
            'description',
            'end',
            'hierarchy',
            'id',
            'items_count',
            'name',
            'members',
            'members_id',
            'owners',
            'owners_id',
            'priority',
            'priority_id',
            'progress',
            'sharings',
            'start',
            'state',
            'tags',
            'tags_id',
            'targets',
            'targets_id',
            'tasks',
            'updated_at',
            'updated_by',
            'url',
        )
        read_only_fields = (
            'created_at',
            'updated_at',
        )

    def create(self, validated_data):
        # Use the 'empty' marker because None may be a valid value to set an empty m2m
        assets = validated_data.pop('assets', empty)
        channels = validated_data.pop('channels', empty)
        members = validated_data.pop('members', empty)
        owners = validated_data.pop('owners', empty)
        tags = validated_data.pop('tags', empty)
        targets = validated_data.pop('targets', empty)

        project = super(ProjectSerializer, self).create(validated_data)

        if assets is not empty:
            project.assets.set(assets or [])
        if channels is not empty:
            project.channels.set(channels or [])
        if members is not empty:
            project.members.set(members or [])
        if owners is not empty:
            project.owners.set(owners or [])
        if tags is not empty:
            project.tags.set(tags or [])
        if targets is not empty:
            project.targets.set(targets or [])

        return project

    def update(self, project, validated_data):
        # Remove m2m data to prevent nested writes errors.
        assets = validated_data.pop('assets', empty)
        channels = validated_data.pop('channels', empty)
        members = validated_data.pop('members', empty)
        owners = validated_data.pop('owners', empty)
        tags = validated_data.pop('tags', empty)
        targets = validated_data.pop('targets', empty)

        for attr, value in validated_data.items():
            setattr(project, attr, value)
        project.save()

        # Set M2M fields
        # When None is used, set an empty M2M with an empty list
        if assets is not empty:
            project.assets.set(assets or [])
        if channels is not empty:
            project.channels.set(channels or [])
        if members is not empty:
            project.members.set(members or [])
        if owners is not empty:
            project.owners.set(owners or [])
        if tags is not empty:
            project.tags.set(tags or [])
        if targets is not empty:
            project.targets.set(targets or [])

        return project


class ProjectListSerializer(serializers.ModelSerializer):
    category = LabelLightSerializer(read_only=True)
    created_by = PilotUserLightSerializer(read_only=True)
    priority = LabelLightSerializer(read_only=True)
    progress = serializers.ReadOnlyField(source='get_progress')
    search_headline = serializers.ReadOnlyField()
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Project
        fields = (
            'category',
            'created_at',
            'created_by',
            'created_by_external_email',
            'end',
            'id',
            'name',
            'priority',
            'progress',
            'search_headline',
            'start',
            'state',
            'url',
        )


class ProjectCalendarSerializer(serializers.ModelSerializer):
    category = LabelLightSerializer(read_only=True)
    text = serializers.ReadOnlyField(source='description')
    title = serializers.ReadOnlyField(source='name')
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Project
        fields = (
            'category',
            'end',
            'id',
            'start',
            'state',
            'targets',
            'text',
            'title',
            'url',
        )


class ProjectChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = (
            'id',
            'name'
        )
