from rest_framework import serializers

from pilot.pilot_users.api.serializers import PilotUserLightSerializer
from pilot.queue.models import JobTracker


class ExportSerializer(serializers.ModelSerializer):
    created_at = serializers.ReadOnlyField()
    created_by = PilotUserLightSerializer(read_only=True)
    in_progress = serializers.ReadOnlyField()
    result_file_name = serializers.ReadOnlyField(source='data.result_file_name')
    result_url = serializers.ReadOnlyField(source='data.result_url')
    state = serializers.ReadOnlyField(source='get_state_display')

    class Meta:
        model = JobTracker
        fields = (
            'created_at',
            'created_by',
            'id',
            'in_progress',
            'result_file_name',
            'result_url',
            'state'
        )
