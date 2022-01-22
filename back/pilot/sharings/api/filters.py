import django_filters
from django_filters.rest_framework import FilterSet

from pilot.channels.models import Channel
from pilot.items.models import Item
from pilot.itemsfilters.models import SavedFilter
from pilot.projects.models import Project
from pilot.sharings.models import Sharing


class SharingFilter(FilterSet):
    channel_id = django_filters.ModelMultipleChoiceFilter(queryset=Channel.objects.all())
    item_id = django_filters.ModelMultipleChoiceFilter(queryset=Item.objects.all())
    project_id = django_filters.ModelMultipleChoiceFilter(queryset=Project.objects.all())
    saved_filter_id = django_filters.ModelMultipleChoiceFilter(queryset=SavedFilter.objects.all())

    class Meta:
        model = Sharing
        fields = ('channel_id', 'item_id', 'project_id', 'saved_filter_id')
