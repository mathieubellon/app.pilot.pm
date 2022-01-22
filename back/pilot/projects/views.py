from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from pilot.desks.utils import connect_to_desk_for_instance_or_404
from pilot.projects.models import Project


@login_required
def projects_app(request, tab='active', project_pk=None):
    """Projects list."""
    # For direct access to project detail, from an external source (link in an email) :
    if project_pk:
        project = get_object_or_404(Project.objects, pk=project_pk)
        connect_to_desk_for_instance_or_404(request, project)

    return render(request, "main_app.html")
