from rest_framework import serializers

from pilot.channels.models import Channel
from pilot.labels.api.serializers import LabelLightSerializer
from pilot.pilot_users.api.serializers import PilotUserLightSerializer


class ChannelUltraLightSerializer(serializers.ModelSerializer):
    """
    Serializer with lighten data, aimed at returning a large number of items into the item calendar/list API
    """
    has_owners = serializers.SerializerMethodField()
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Channel
        fields = (
            'has_owners',
            'name',
            'url',
        )

    def get_has_owners(self, channel):
        # owners are prefetched, so the .all() won't hit the db
        return bool(channel.owners.all())


class ChannelLightSerializer(serializers.ModelSerializer):
    has_owners = serializers.SerializerMethodField()
    owners = PilotUserLightSerializer(many=True, read_only=True)
    type = LabelLightSerializer(read_only=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Channel
        fields = (
            'description',
            'has_owners',
            'name',
            'id',
            'name',
            'owners',
            'type',
            'url',
        )

    def get_has_owners(self, channel):
        return bool(channel.owners.all())



