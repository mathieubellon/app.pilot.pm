from rest_framework import serializers

from pilot.targets.models import Target


class TargetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Target
        fields = (
            'description',
            'id',
            'name',
        )


class TargetUltraLightSerializer(serializers.ModelSerializer):
    """
    Serializer with lighten data, aimed at returning a large number of items into the item calendar/list API
    """
    class Meta:
        model = Target
        fields = (
            'name',
        )


class TargetChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Target
        fields = (
            'id',
            'name'
        )
