import django_filters
from django_filters.rest_framework import FilterSet


from pilot.channels.models import Channel
from pilot.item_types.models import ItemType
from pilot.items.api.filters import ItemOrderingFilter, LANGUAGES_CHOICES
from pilot.items.models import Item
from pilot.labels.models import Label
from pilot.pilot_users.models import PilotUser
from pilot.projects.api.filters import EndDateFilter, StartDateFilter
from pilot.projects.models import Project
from pilot.targets.models import Target
from pilot.utils.search import SearchFilterSetMixin
from pilot.workflow.models import WorkflowState


class ChannelFilter(SearchFilterSetMixin, FilterSet):
    created_by = django_filters.ModelMultipleChoiceFilter(
        queryset=PilotUser.objects.all()
    )

    owners = django_filters.ModelMultipleChoiceFilter(
        queryset=PilotUser.objects.all()
    )

    state = django_filters.MultipleChoiceFilter(
        choices=Project.STATES_CHOICES
    )

    type = django_filters.ModelMultipleChoiceFilter(
        queryset=Label.objects.all()
    )

    updated_by = django_filters.ModelMultipleChoiceFilter(
        queryset=PilotUser.objects.all()
    )

    order_by = django_filters.OrderingFilter(
        fields=('name', 'created_at', 'updated_at')
    )

    class Meta:
        model = Channel
        fields = (
            'q', 'q_partial',
            'created_by', 'id',  'owners', 'state', 'type', 'updated_by'
        )


class ProjectFilter(SearchFilterSetMixin, FilterSet):
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

    order_by = django_filters.OrderingFilter(
        fields=('created_at', 'end', 'id', 'name', 'priority', 'start', 'updated_at')
    )

    class Meta:
        model = Project
        fields = (
            'q', 'q_partial',
            'category', 'channels', 'created_at', 'created_by',
            'end', 'owners',
            'start', 'state', 'tags', 'targets', 'type',
            'updated_by',
        )


class ItemFilter(SearchFilterSetMixin, FilterSet):
    channels = django_filters.ModelMultipleChoiceFilter(
        queryset=Channel.objects.all()
    )

    channel_owners = django_filters.ModelMultipleChoiceFilter(
        field_name='channels__owners',
        queryset=PilotUser.objects.all()
    )

    created_at = django_filters.DateFilter(
        lookup_expr='gte'
    )

    created_by = django_filters.ModelMultipleChoiceFilter(
        queryset=PilotUser.objects.all()
    )

    id = django_filters.NumberFilter(
        method='filter_id'
    )

    item_type = django_filters.ModelChoiceFilter(
        queryset=ItemType.objects.all()
    )

    language = django_filters.TypedMultipleChoiceFilter(
        choices=LANGUAGES_CHOICES,
        coerce=lambda lang: '' if lang == 'blank' else lang
    )

    master_translation = django_filters.ModelMultipleChoiceFilter(
        queryset=Item.objects.all(),
    )

    members = django_filters.ModelMultipleChoiceFilter(
        field_name='project__members',
        queryset=PilotUser.objects.all()
    )

    owners = django_filters.ModelMultipleChoiceFilter(
        queryset=PilotUser.objects.all()
    )

    project = django_filters.ModelMultipleChoiceFilter(
        queryset=Project.objects.all()
    )

    project_state = django_filters.MultipleChoiceFilter(
        field_name='project__state',
        choices=Project.STATES_CHOICES
    )

    project_owners = django_filters.ModelMultipleChoiceFilter(
        field_name='project__owners',
        queryset=PilotUser.objects.all()
    )

    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Label.objects.all()
    )

    targets = django_filters.ModelMultipleChoiceFilter(
        queryset=Target.objects.all()
    )

    task_assignees = django_filters.ModelMultipleChoiceFilter(
        field_name='tasks__assignees',
        queryset=PilotUser.objects.all()
    )

    updated_by = django_filters.ModelMultipleChoiceFilter(
        queryset=PilotUser.objects.all()
    )

    workflow_state = django_filters.ModelMultipleChoiceFilter(
        queryset=WorkflowState.objects.all()
    )

    # Duplicate fields needed for the calendar filter syntax
    item_owners = django_filters.ModelMultipleChoiceFilter(
        field_name='owners',
        queryset=PilotUser.objects.all()
    )
    item_tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags',
        queryset=Label.objects.all()
    )

    order_by = ItemOrderingFilter(
        fields=(
            'channels__name', 'created_at', 'id', 'item_title',
            'project__name', 'publication_dt', 'updated_at', 'workflow_state__order'
        )
    )

    class Meta:
        model = Item
        fields = (
            'q', 'q_partial',
            'channels', 'channel_owners',
            'created_at', 'created_by',
            'id', 'item_owners', 'item_type', 'item_tags', 'language',
            'master_translation', 'members', 'owners', 'project', 'project_state',
            'tags', 'targets', 'task_assignees', 'updated_by', 'workflow_state',
        )

    def filter_id(self, qs, name, value):
        if self.request:
            return qs.filter(id__in=self.request.GET.getlist('id'))
        else:
            return qs.filter(id=value)



