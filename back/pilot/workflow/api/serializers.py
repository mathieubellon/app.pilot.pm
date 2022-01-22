from rest_framework import serializers

from pilot.workflow.models import WorkflowState


class WorkflowStateLightSerializer(serializers.ModelSerializer):
    """
    Serializer with lighten data, aimed at returning a large number of items into the item calendar/list API
    """

    class Meta:
        model = WorkflowState
        fields = (
            'id',  # We need the id in item lsits to now which workflow_state is selected
            'color',
            'label',
        )


class WorkflowStateSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkflowState
        fields = (
            'color',
            'id',
            'label',
            'order',
        )
