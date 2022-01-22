from rest_framework import serializers

from pilot.wiki.models import WikiPage


class WikiPageSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = WikiPage
        fields = (
            'content',
            'id',
            'is_home_page',
            'name',
            'url',
        )
        read_only_fields = (
            'is_home_page',
        )
