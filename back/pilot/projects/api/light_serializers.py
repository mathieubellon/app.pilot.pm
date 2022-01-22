from rest_framework import serializers

from pilot.labels.api.serializers import LabelLightSerializer
from pilot.projects.models import Project


class ProjectLightSerializer(serializers.ModelSerializer):
    """
    Serializer with lighten data, aimed at returning a large number of items into the item calendar/list API
    """
    category = LabelLightSerializer(read_only=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Project
        fields = (
            'category',
            'id',
            'name',
            'url',
        )
