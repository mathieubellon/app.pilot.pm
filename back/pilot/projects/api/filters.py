import django_filters
from django.db.models import Q
from django_filters.constants import EMPTY_VALUES
from django_filters.rest_framework import FilterSet

from pilot.channels.models import Channel
from pilot.labels.models import Label
from pilot.pilot_users.models import PilotUser
from pilot.projects.models import Project
from pilot.targets.models import Target
from pilot.utils.api.filters import MultipleFilter
from pilot.utils.search import SearchFilterSetMixin


class StartDateFilter(django_filters.DateFilter):
    # When filtering on an end date, matching projects are those who start before this end date
    def filter(self, queryset, start_date):
        if start_date in EMPTY_VALUES:
            return queryset
        return queryset.filter(
            Q(end__gte=start_date)
            |
            Q(end=None, start__gte=start_date)
            |
            Q(start=None, end__gte=start_date)
        )


class EndDateFilter(django_filters.DateFilter):
    # When filtering on a start date, matching projects are those who end after this start date
    def filter(self, queryset, end_date):
        if end_date in EMPTY_VALUES:
            return queryset
        return queryset.filter(
            Q(start__lte=end_date)
            |
            Q(start=None, end__lte=end_date)
            |
            Q(end=None, start__lte=end_date)
        )


class ProjectFilter(SearchFilterSetMixin, FilterSet):
    # This is used in the calendar to filter by id
    project = MultipleFilter(field_name="id")

    channels = django_filters.ModelMultipleChoiceFilter(
        queryset=Channel.objects.all()
    )

    channels_owners = django_filters.ModelMultipleChoiceFilter(
        field_name='channels__owners',
        queryset=PilotUser.objects.all()
    )

    created_at = django_filters.DateFilter(
        lookup_expr='gte'
    )

    created_by = django_filters.ModelMultipleChoiceFilter(
        queryset=PilotUser.objects.all()
    )

    end = EndDateFilter()

    category = django_filters.ModelMultipleChoiceFilter(
        queryset=Label.objects.all()
    )

    members = django_filters.ModelMultipleChoiceFilter(
        queryset=PilotUser.objects.all()
    )

    owners = django_filters.ModelMultipleChoiceFilter(
        queryset=PilotUser.objects.all()
    )

    priority = django_filters.ModelMultipleChoiceFilter(
        queryset=Label.objects.all()
    )

    start = StartDateFilter()

    state = django_filters.MultipleChoiceFilter(
        choices=Project.STATES_CHOICES
    )

    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Label.objects.all()
    )

    targets = django_filters.ModelMultipleChoiceFilter(
        queryset=Target.objects.all()
    )

    type = django_filters.ModelMultipleChoiceFilter(
        queryset=Label.objects.all()
    )

    updated_by = django_filters.ModelMultipleChoiceFilter(
        queryset=PilotUser.objects.all()
    )

    # Duplicate fields needed for the calendar filter syntax
    project_owners = django_filters.ModelMultipleChoiceFilter(
        field_name='owners',
        queryset=PilotUser.objects.all()
    )

    project_tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags',
        queryset=Label.objects.all()
    )

    order_by = django_filters.OrderingFilter(
        fields=('created_at', 'end', 'id', 'name', 'priority', 'start', 'updated_at')
    )

    class Meta:
        model = Project
        fields = (
            'q', 'q_partial',
            'category', 'channels', 'created_at', 'created_by',
            'end', 'owners', 'project_owners', 'project_tags',
            'start', 'state', 'tags', 'targets', 'type',
            'updated_by',
        )
