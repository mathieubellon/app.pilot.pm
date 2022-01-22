import django_filters
from django_filters.rest_framework import FilterSet

from rest_framework import viewsets
from rest_framework.decorators import action

from pilot.targets.api.serializers import TargetChoiceSerializer, TargetSerializer
from pilot.targets.models import Target
from pilot.utils import api as api_utils


class TargetFilter(FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    order_by = django_filters.OrderingFilter(
        fields=('id', 'name', 'created_at', 'updated_at')
    )

    class Meta:
        model = Target
        fields = ('name',)


class TargetsViewset(api_utils.ActivityModelMixin,
                     viewsets.ModelViewSet):
    serializer_class = TargetSerializer
    permission_classes = [
        api_utils.DeskPermission,
        api_utils.IsAdminOrReadOnlyPermission
    ]
    filter_class = TargetFilter
    default_ordering = 'name'

    def get_queryset(self):
        return (Target.objects
                .filter(desk=self.request.desk)
                # Default ordering, that may be overrided by the query params
                .order_by(self.default_ordering))

    def perform_create(self, serializer):
        serializer.save(
            desk=self.request.desk,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=False, pagination_class=None, serializer_class=TargetChoiceSerializer)
    def choices(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
