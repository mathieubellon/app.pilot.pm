from rest_framework import serializers
from rest_framework.fields import empty

from pilot.assets.api.serializers import AssetLightSerializer
from pilot.channels.api.light_serializers import ChannelLightSerializer
from pilot.channels.models import Channel
from pilot.labels.api.serializers import LabelLightSerializer
from pilot.pilot_users.api.serializers import PilotUserLightSerializer
from pilot.sharings.api.serializers_base import LinkedSharingSerializer
from pilot.tasks.api.serializers_base import LinkedTaskSerializer
from pilot.utils.api.serializers import SmartPrimaryKeyRelatedField


class ChannelSerializer(serializers.ModelSerializer):
    assets = AssetLightSerializer(many=True, read_only=True)
    created_by = PilotUserLightSerializer(read_only=True)
    # items_count is annotated by ProjelQuerySet.detail_api_prefetch
    items_count = serializers.ReadOnlyField()
    owners = PilotUserLightSerializer(many=True, read_only=True)
    owners_id = SmartPrimaryKeyRelatedField(source='owners', many=True, required=False, allow_null=True)
    sharings = LinkedSharingSerializer(many=True, read_only=True)
    tasks = LinkedTaskSerializer(many=True, required=False, read_only=True)
    type = LabelLightSerializer(read_only=True)
    type_id = SmartPrimaryKeyRelatedField(required=False, allow_null=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Channel
        fields = (
            'assets',
            'created_at',
            'created_by',
            'description',
            'hierarchy',
            'id',
            'items_count',
            'name',
            'owners',
            'owners_id',
            'sharings',
            'state',
            'type',
            'type_id',
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
        owners = validated_data.pop('owners', empty)

        channel = super(ChannelSerializer, self).create(validated_data)

        if assets is not empty:
            channel.assets.set(assets or [])
        if owners is not empty:
            channel.owners.set(owners or [])

        return channel

    def update(self, channel, validated_data):
        # Remove m2m data to prevent nested writes errors.
        assets = validated_data.pop('assets', empty)
        owners = validated_data.pop('owners', empty)

        for attr, value in validated_data.items():
            setattr(channel, attr, value)
        channel.save()

        # Set M2M fields
        # When None is used, set an empty M2M with an empty list
        if assets is not empty:
            channel.assets.set(assets or [])
        if owners is not empty:
            channel.owners.set(owners or [])

        return channel


class ChannelListSerializer(serializers.ModelSerializer):
    search_headline = serializers.ReadOnlyField()
    type = LabelLightSerializer(read_only=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Channel
        fields = (
            'id',
            'name',
            'search_headline',
            'type',
            'url',
        )


class ChannelForItemDetailSerializer(ChannelLightSerializer):
    """
    Serializer with data for the ItemDetail view
    """

    class Meta:
        model = Channel
        fields = (
            'description',
            'hierarchy',
            'name',
            'id',
            'name',
            'url',
        )


class ChannelChoiceSerializer(serializers.ModelSerializer):
    type = LabelLightSerializer(read_only=True)

    class Meta:
        model = Channel
        fields = (
            'id',
            'hierarchy',
            'name',
            'type',
        )
