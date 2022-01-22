from rest_framework import viewsets

from pilot.integrations.api.serializers import ApiTokenSerializer
from pilot.integrations.models import ApiToken
from pilot.utils import api as api_utils


class ApiTokenViewset(api_utils.ActivityModelMixin,
                     viewsets.ModelViewSet):
    serializer_class = ApiTokenSerializer
    permission_classes = [
        api_utils.DeskPermission,
        api_utils.IsAdminPermission
    ]
    default_ordering = 'name'

    def get_queryset(self):
        return ApiToken.objects.filter(desk=self.request.desk)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            desk=self.request.desk
        )


