import json

from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db.models.expressions import OuterRef, Subquery
from django.utils.translation import ugettext_lazy as _

import django_filters
from django_filters.rest_framework import FilterSet
from django_filters.constants import EMPTY_VALUES

from pilot.channels.models import Channel
from pilot.item_types.models import ItemType
from pilot.items.models import Item
from pilot.labels.models import Label
from pilot.pilot_users.models import PilotUser
from pilot.projects.models import Project
from pilot.targets.models import Target
from pilot.tasks.models import Task
from pilot.utils import pilot_languages
from pilot.utils.projel.hierarchy import get_items_in_folder
from pilot.utils.search import SearchFilterSetMixin
from pilot.workflow.models import WorkflowState

# Adding an explicit empty value
LANGUAGES_CHOICES = (('blank', _("Aucun")),) + pilot_languages.LANGUAGES_CHOICES


class ItemOrderingFilter(django_filters.OrderingFilter):
    """
    A special OrderingFilter that can handle ordering on 'publication_dt' field
    which has been moved to Task.deadline
    """
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        ordering = []
        for param in value:
            if 'item_title' in param:
                qs = qs.annotate(item_title=KeyTextTransform('title', 'json_content'))

            # simulate 'publication_dt' field which has been moved to Task.deadline with an annotation
            if 'publication_dt' in param:
                # The SubQuery syntax is documented here :
                # https://docs.djangoproject.com/en/1.11/ref/models/expressions/#subquery-expressions
                publication_task = Task.objects.filter(item=OuterRef('pk'), is_publication=True)
                qs = qs.annotate(publication_dt=Subquery(publication_task.values('deadline')[:1]))

            ordering.append(self.get_ordering_value(param))

        return qs.order_by(*ordering)


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

    folder = django_filters.Filter(
        method='filter_folder'
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
            'folder',
            'id', 'item_owners', 'item_type', 'item_tags', 'language',
            'members', 'owners', 'project', 'project_state',
            'tags', 'targets', 'task_assignees', 'updated_by', 'workflow_state',
        )

    def filter_id(self, queryset, name, value):
        if self.request:
            return queryset.filter(id__in=self.request.GET.getlist('id'))
        else:
            return queryset.filter(id=value)

    def filter_folder(self, queryset, name, value):
        if hasattr(self.request, 'project_id'):
            projel = Project.objects.get(id=self.request.project_id)
        elif hasattr(self.request, 'channel_id'):
            projel = Channel.objects.get(id=self.request.channel_id)
        else:
            raise Exception("folder filter can only be used with list_for_project or list_for_channel")

        folder_path = json.loads(value)
        item_ids = get_items_in_folder(projel.hierarchy, folder_path)
        return queryset.filter(id__in=item_ids)
