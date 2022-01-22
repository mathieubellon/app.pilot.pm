from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_202_ACCEPTED

from pilot.accounts.usage_limit import ProjectUsageLimit
from pilot.projects.api.filters import ProjectFilter
from pilot.projects.api.serializers import ProjectCalendarSerializer, ProjectChoiceSerializer, ProjectListSerializer, \
    ProjectSerializer
from pilot.projects.jobs import CopyProjectJob, AllProjectsXLSExportJob
from pilot.projects.models import Project
from pilot.utils import api as api_utils, states
from pilot.utils.projel.api import ProjelViewSet
from pilot.utils.projel.hierarchy import HierarchyConsistencyJob


class ProjectViewSet(ProjelViewSet):
    """
    A viewset to work with Projects endpoint
    """
    serializer_class = ProjectSerializer
    filter_class = ProjectFilter
    base_queryset = Project.objects

    # ===================
    # Create / Update
    # ===================

    def perform_update(self, serializer):
        old_state = serializer.instance.state
        new_state = serializer.validated_data.get('state')

        # If the project is re-activated, check the usage limit
        if old_state == states.STATE_CLOSED and new_state == states.STATE_ACTIVE:
            ProjectUsageLimit(self.request.desk).check_limit()

        project = serializer.save(updated_by=self.request.user)

        # If the project is accepted, then the creator become the owner
        # ( https://gitlab.com/matthieubellon/pilot/issues/827 )
        if old_state == states.STATE_IDEA and new_state == states.STATE_ACTIVE and project.created_by:
            project.owners.add(project.created_by)

    # ===================
    # Custom routes
    # ===================

    @action(
        detail=False,
        base_queryset=Project.active_objects,
        serializer_class=ProjectListSerializer
    )
    def active(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(
        detail=False,
        base_queryset=Project.unconfirmed_objects,
        serializer_class=ProjectListSerializer
    )
    def idea(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(
        detail=False,
        base_queryset=Project.closed_objects,
        serializer_class=ProjectListSerializer
    )
    def closed(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(
        detail=False,
        base_queryset=Project.active_objects,
        serializer_class=ProjectChoiceSerializer,
        pagination_class=None,
        default_ordering='name'  # On choices, order by 'name' by default
    )
    def choices(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(detail=False, methods=['PUT'])
    def export(self, request, *args, **kwargs):
        AllProjectsXLSExportJob.launch_r(self.request, timeout='30m')
        return Response(status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['PUT'])
    def copy(self, request, *args, **kwargs):
        """
        Launch a job to copy a project into a new project.

        Available options :
        - A new name
        - What should we copy (metadata, items, m2m...)
        """
        project = self.get_object()
        new_project = Project.objects.create(
            desk=self.request.desk,
            created_by=self.request.user,
            name=self.request.data.get('name', project.name),
            state=states.STATE_COPY,
            copied_from=project
        )
        CopyProjectJob.launch_r(
            self.request,
            source_project=project,
            new_project=new_project,
            copy_params=self.request.data.get('copy_params', {}),
        )
        return Response(self.get_serializer(new_project).data, status=HTTP_202_ACCEPTED)

    @action(detail=True, methods=['PUT'])
    def remove_items(self,  request, *args, **kwargs):
        project = self.get_object()
        item_ids = request.data.get('itemIds')
        project.items.filter(id__in=item_ids).update(project=None)
        HierarchyConsistencyJob.launch_r(self.request, project)
        return Response(status=HTTP_202_ACCEPTED)


class CalendarProjectListView(ListAPIView):
    serializer_class = ProjectCalendarSerializer
    permission_classes = [
        api_utils.DeskPermission
    ]
    filter_class = ProjectFilter

    def get_queryset(self):
        return (
            Project.active_objects
            .filter(desk=self.request.desk)
            .filter_by_permissions(self.request.user)
            .exclude(start=None)
            .exclude(end=None)
            .prefetch_related('targets')
        )


class SharedCalendarProjectList(api_utils.SharedApiMixin, CalendarProjectListView):
    """
    Gets a list of Item objects related to an PublicSharedFilter object and suitable for display in a calendar.
    Public API method: accessible by an anonymous user.
    """
    permission_classes = [
        AllowAny
    ]


ChannelViewSet = ProjectViewSet
