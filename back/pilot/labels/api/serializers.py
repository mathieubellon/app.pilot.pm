from rest_framework import serializers

from pilot.labels.models import Label


class LabelLightSerializer(serializers.ModelSerializer):

    class Meta:
        model = Label
        fields = (
            'color',
            'background_color',
            'id',
            'name',
            'target_type',  # We ABSOLUTELY need this field for Label.vue.listUrl() to work
        )


class LabelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Label
        fields = (
            'color',
            'background_color',
            'id',
            'name',
            'order',
            'target_type'
        )
