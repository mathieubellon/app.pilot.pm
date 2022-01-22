from django.http import Http404

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from pilot.list_config.api.serializers import ListConfigSerializer
from pilot.list_config.models import ListConfig
from pilot.utils import api as api_utils
from pilot.utils.api import SharedApiMixin


class ListConfigViewSet(viewsets.ModelViewSet):
    serializer_class = ListConfigSerializer
    permission_classes = [
        api_utils.DeskPermission
    ]
    lookup_field = 'name'

    def get_queryset(self):
        return ListConfig.objects.filter(desk=self.request.desk)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get_object(self):
        try:
            return super(ListConfigViewSet, self).get_object()
        except Http404:
            return ListConfig.objects.create(
                desk=self.request.desk,
                name=self.kwargs['name'],
                created_by=self.request.user
            )


class SharedListConfigViewSet(SharedApiMixin, ListConfigViewSet):
    permission_classes = [
        AllowAny
    ]
    # Read-only access on the shared API
    allowed_methods = ['GET']
