from django.db.models import F as Field
from django.db import transaction

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from pilot.utils import api as api_utils
from pilot.workflow.api.serializers import WorkflowStateSerializer
from pilot.workflow.models import WorkflowState


class WorkflowStateViewSet(api_utils.ActivityModelMixin,
                           viewsets.ModelViewSet):
    serializer_class = WorkflowStateSerializer
    permission_classes = [
        api_utils.DeskPermission,
        api_utils.IsAdminOrReadOnlyPermission
    ]

    def get_queryset(self):
        return WorkflowState.objects.filter(desk=self.request.desk)

    def perform_create(self, serializer):
        serializer.save(
            desk=self.request.desk,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        with transaction.atomic():
            # Update other states order
            WorkflowState.objects.filter(
                desk=self.request.desk,
                order__gt=instance.order
            ).update(order=Field('order')-1)
            # Delete the state
            instance.delete()

    @action(detail=False, methods=['POST'])
    def set_order(self, request, *args, **kwargs):
        with transaction.atomic():
            queryset = self.get_queryset()
            for state_order in request.data:
                queryset.filter(id=state_order['id']).update(order=state_order['order'])

        return Response(self.get_serializer(self.get_queryset(), many=True).data)
