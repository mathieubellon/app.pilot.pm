import django_filters
from django_filters.rest_framework import FilterSet

from pilot.itemsfilters.models import InternalSharedFilter, SavedFilter


class SavedFilterFilter(FilterSet):

    order_by = django_filters.OrderingFilter(
        fields=('title',)
    )

    class Meta:
        model = SavedFilter
        fields = ('type',)


class InternalSharedFilterFilter(FilterSet):

    class Meta:
        model = InternalSharedFilter
        fields = ('saved_filter',)
