from django.utils.translation import ugettext_lazy as _

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from pilot.utils import api as api_utils
from pilot.wiki.api.serializers import WikiPageSerializer
from pilot.wiki.models import WikiPage


class WikiPageViewset(api_utils.ActivityModelMixin,
                     viewsets.ModelViewSet):
    serializer_class = WikiPageSerializer
    permission_classes = [
        api_utils.DeskPermission,
        api_utils.IsAdminOrReadOnlyPermission
    ]
    default_ordering = 'name'

    def get_queryset(self):
        return (
            WikiPage.objects
            .filter(desk=self.request.desk)
            # Default ordering, that may be overrided by the query params
            .order_by(self.default_ordering)
        )

    def perform_create(self, serializer):
        serializer.save(
            desk=self.request.desk,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, wiki_page):
        """
        We don't actually destroy the instance, but set its "hidden" flag to True
        """
        if wiki_page.is_home_page:
            raise PermissionDenied(_("Impossible de supprimer la page d'accueil du wiki"))

        wiki_page.hide(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def home(self, request, *args, **kwargs):
        instance = self.get_queryset().get(is_home_page=True)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
