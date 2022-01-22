from rest_framework import serializers

from pilot.list_config.models import ListConfig


class ListConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = ListConfig
        fields = (
            'columns',
            'name',
            'ordering'
        )
