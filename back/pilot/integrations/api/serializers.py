from rest_framework import serializers

from pilot.integrations.models import ApiToken


class ApiTokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(read_only=True)

    class Meta:
        model = ApiToken
        fields = (
            'id',
            'name',
            'description',
            'token',
        )


