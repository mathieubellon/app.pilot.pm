from rest_framework.fields import empty
from rest_framework import serializers

from pilot.channels.api.light_serializers import ChannelLightSerializer
from pilot.items.api.light_serializers import ItemLightSerializer
from pilot.projects.api.light_serializers import ProjectLightSerializer
from pilot.tasks.api.serializers_base import BaseTaskSerializer
from pilot.tasks.models import Task, TaskGroup
from pilot.utils.api.serializers import SmartPrimaryKeyRelatedField


class TaskSerializer(BaseTaskSerializer):
    channel = ChannelLightSerializer(read_only=True)
    item = ItemLightSerializer(read_only=True)
    project = ProjectLightSerializer(read_only=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Task
        fields = BaseTaskSerializer.Meta.fields + (
            'channel',
            'item',
            'project',
            'url',
        )

    def create(self, validated_data):
        # Use the 'empty' marker because None may be a valid value to set an empty m2m
        assignees = validated_data.pop('assignees', empty)

        task = super(TaskSerializer, self).create(validated_data)

        # Set M2M fields
        # When None is used, set an empty M2M with an empty list
        if assignees is not empty:
            task.assignees.set(assignees or [])

        return task

    def update(self, instance, validated_data):
        # Use the 'empty' marker because None may be a valid value to set an empty m2m
        assignees = validated_data.pop('assignees', empty)

        task = super(TaskSerializer, self).update(instance, validated_data)

        # Set M2M fields
        # When None is used, set an empty M2M with an empty list
        if assignees is not empty:
            task.assignees.set(assignees or [])

        return task


class TaskTemplateSerializer(BaseTaskSerializer):
    task_group_id = SmartPrimaryKeyRelatedField(required=True, allow_null=False)

    class Meta:
        model = Task
        fields = (
            'assignees',
            'assignees_id',
            'can_be_hidden',
            'id',
            'is_publication',
            'name',
            'order',
            # 'show_in_publishing_calendar',
            'task_group_id',
        )


class TaskGroupSerializer(serializers.ModelSerializer):
    tasks = TaskTemplateSerializer(many=True, read_only=True)

    class Meta:
        model = TaskGroup
        fields = (
            'id',
            'description',
            'name',
            'tasks',
        )


class TaskGroupLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskGroup
        fields = (
            'description',
            'id',
            'name',
        )
