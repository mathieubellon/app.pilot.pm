from rest_framework import serializers

from pilot.items.models import Item
from pilot.projects.models import Project
from pilot.utils.pilot_languages import LANGUAGES_CHOICES


class ItemSearchDocTypeSerializer(serializers.ModelSerializer):
    project = serializers.CharField()
    channels = serializers.StringRelatedField(read_only=True, many=True)
    content = serializers.SerializerMethodField()
    desk_id = serializers.ReadOnlyField()
    language = serializers.ChoiceField(
        choices=LANGUAGES_CHOICES,
        source='get_language_display'
    )
    tags = serializers.SerializerMethodField()
    targets = serializers.StringRelatedField(read_only=True, many=True)
    title = serializers.SerializerMethodField()
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Item
        fields = (
            'id',
            'project',
            'channels',
            'content',
            'desk_id',
            'hidden',
            'in_trash',
            'language',
            'publication_dt',
            'tags',
            'targets',
            'title',
            'url',
        )

    def get_title(self, item):
        title = item.title
        # Some users use the title fields to organise their content
        # and write title with underscores (eg. Global_AllActivities_Group)
        # We need to break that and allow ES to index each word
        if title and '_' in title:
            title = title.replace('_', ' ')
        return title

    def get_content(self, item):
        return '\n'.join(item.get_search_values()[1:])

    def get_tags(self, item):
        return [tag.name for tag in item.tags.all()]


class ProjectSearchDocTypeSerializer(serializers.ModelSerializer):
    channels = serializers.StringRelatedField(read_only=True, many=True)
    description = serializers.SerializerMethodField()
    desk_id = serializers.ReadOnlyField()
    tags = serializers.SerializerMethodField()
    targets = serializers.StringRelatedField(read_only=True, many=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Project
        fields = (
            'id',
            'channels',
            'description',
            'desk_id',
            'hidden',
            'name',
            'tags',
            'targets',
            'url',
        )

    def get_tags(self, item):
        return [tag.name for tag in item.tags.all()]

    def get_description(self, project):
        return project.get_search_values()[1]
