from rest_framework import viewsets

from pilot.favorites.api.serializers import FavoriteSerializer
from pilot.favorites.models import Favorite
from pilot.utils import api as api_utils


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [
        api_utils.DeskPermission,
    ]

    def get_queryset(self):
        return Favorite.objects.filter(
            desk=self.request.desk,
            user=self.request.user
        ).prefetch_related('target')

    # ===================
    # Create / Update
    # ===================

    def perform_create(self, serializer):
        return serializer.save(
            desk=self.request.desk,
            user=self.request.user
        )
