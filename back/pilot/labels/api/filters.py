from django_filters.rest_framework import FilterSet

from pilot.labels.models import Label


class LabelFilter(FilterSet):
    class Meta:
        model = Label
        fields = ('target_type', )
