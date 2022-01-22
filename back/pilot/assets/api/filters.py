import django_filters
from django_filters.rest_framework import FilterSet

from pilot.assets.models import Asset, AssetRight
from pilot.labels.models import Label
from pilot.pilot_users.models import PilotUser
from pilot.utils.search import SearchFilterSetMixin


class AssetFilter(SearchFilterSetMixin, FilterSet):
    created_by = django_filters.ModelMultipleChoiceFilter(queryset=PilotUser.objects.all())
    folder = django_filters.ModelMultipleChoiceFilter(queryset=Label.objects.all())
    title = django_filters.CharFilter()
    updated_by = django_filters.ModelMultipleChoiceFilter(queryset=PilotUser.objects.all())

    order_by = django_filters.OrderingFilter(
        fields=('id', 'title', 'filetype', 'created_at', 'updated_at')
    )

    class Meta:
        model = Asset
        fields = ('q', 'q_partial', 'created_by', 'folder', 'filetype', 'title', 'updated_by')


class AssetRightFilter(FilterSet):
    class Meta:
        model = AssetRight
        fields = ('asset', )
