from rest_framework import serializers

from pilot.favorites.models import Favorite
from pilot.utils.api.serializers import SmartPrimaryKeyRelatedField


class FavoriteSerializer(serializers.ModelSerializer):
    target_content_type_id = SmartPrimaryKeyRelatedField(restrict_desk=False)
    target_name = serializers.CharField(read_only=True)
    target_url = serializers.CharField(read_only=True)

    class Meta:
        model = Favorite
        fields = (
            'id',
            'target_content_type_id',
            'target_name',
            'target_object_id',
            'target_url',
        )
