import uuid

from django.http import JsonResponse
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.status import HTTP_202_ACCEPTED

from pilot.accounts.models import SubscriptionPlan
from pilot.desks.api.export_serializers import ExportSerializer
from pilot.desks.api.serializers import DeskSerializer
from pilot.desks.jobs import DeskExportFinalizeJob, launch_desk_export
from pilot.desks.models import Desk
from pilot.desks.utils import connect_to_desk
from pilot.pilot_users.models import PERMISSION_ADMINS, UserInDesk
from pilot.queue.models import JobTracker
from pilot.utils import api as api_utils
from pilot.utils.s3 import get_s3_signature_v4


class DeskViewset(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    serializer_class = DeskSerializer
    permission_classes = [
        api_utils.DeskPermission,
        api_utils.IsAdminOrReadOnlyPermission
    ]
    queryset = Desk.objects.none() # For swagger

    def get_object(self):
        return self.request.desk

    def perform_create(self, serializer):
        if not self.request.user.permissions.is_organization_admin:
            raise PermissionDenied("Only the organization admin can create new desks")

        desk = serializer.save(
            created_by=self.request.user,
            organization=self.request.organization,
            subscription_plan=SubscriptionPlan.get_trial_subscription(),
            is_active=True
        )
        UserInDesk.objects.create(
            desk=desk,
            user=self.request.user,
            permission=PERMISSION_ADMINS
        )
        connect_to_desk(desk, self.request)

    def perform_update(self, serializer):
        logo_kwargs = {}
        # The logo param may be present or not, and if present in may be null.
        # In case of an update, we'll get the image url
        # In case of a delete, we'll get 'DELETE'
        logo = self.request.data.get('logo')
        if logo:
            logo_kwargs['logo'] = None if (logo == 'DELETE') else logo

        serializer.save(
            updated_by=self.request.user,
            **logo_kwargs
        )

    @action(detail=False, methods=['POST'])
    def get_s3_signature_for_logo(self, request):
         # Generate a random uuid for the file name, to avoid guessing by desk id
        s3_path = 'logos/{0}'.format(uuid.uuid4())
        content_type = request.data.get('contentType')
        signature_data = get_s3_signature_v4(s3_path, content_type)
        return JsonResponse(signature_data)


class ExportViewset(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = ExportSerializer
    permission_classes = [
        api_utils.DeskPermission,
        api_utils.IsAdminPermission
    ]

    def get_queryset(self):
        return (JobTracker.objects.filter(
            desk=self.request.desk,
            job_type=DeskExportFinalizeJob.job_type
        )
        .order_by('-created_at'))

    def create(self, request, *args, **kwargs):
        launch = launch_desk_export(request)
        serializer = self.get_serializer(launch['job_tracker'])
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_202_ACCEPTED, headers=headers)
