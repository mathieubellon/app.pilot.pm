from rest_framework import serializers

from pilot.messaging.models import Message


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer with lighten data, aimed at returning a large number of items into the item calendar/list API
    """
    class Meta:
        model = Message
        fields = (
            'content',
            'id',
            'type',
        )
        read_only_fields = (
            'content',
            'type',
        )
