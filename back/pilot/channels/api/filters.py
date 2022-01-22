import django_filters
from django_filters.rest_framework import FilterSet

from pilot.channels.models import Channel
from pilot.labels.models import Label
from pilot.pilot_users.models import PilotUser
from pilot.utils.search import SearchFilterSetMixin


class ChannelFilter(SearchFilterSetMixin, FilterSet):
    created_by = django_filters.ModelMultipleChoiceFilter(
        queryset=PilotUser.objects.all()
    )

    owners = django_filters.ModelMultipleChoiceFilter(
        queryset=PilotUser.objects.all()
    )

    type = django_filters.ModelMultipleChoiceFilter(
        queryset=Label.objects.all()
    )

    updated_by = django_filters.ModelMultipleChoiceFilter(
        queryset=PilotUser.objects.all()
    )

    order_by = django_filters.OrderingFilter(
        fields=('created_at', 'name', 'updated_at')
    )

    class Meta:
        model = Channel
        fields = (
            'q', 'q_partial',
            'created_by', 'owners', 'type', 'updated_by'
        )
