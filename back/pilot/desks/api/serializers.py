from rest_framework import serializers

from pilot.desks.models import Desk


class DeskSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(read_only=True)

    class Meta:
        model = Desk
        fields = (
            'allowed_languages',
            'creation_forms_fields_visibles_by_default',
            'id',
            'item_languages_enabled',
            'logo',
            'name',
            'private_items_enabled',
        )
