from django.http import JsonResponse, HttpResponseForbidden
from django.utils.encoding import force_text
from django.shortcuts import render

from pilot.channels.api.api import ChannelViewSet
from pilot.favorites.api.api import FavoriteViewSet
from pilot.item_types.api.api import ItemTypeViewSet
from pilot.pilot_users.api.api import UsersMeViewSet, UsersViewSet, TeamViewSet
from pilot.projects.api.api import ProjectViewSet
from pilot.targets.api.api import TargetsViewset
from pilot.tasks.api.serializers import TaskGroupLightSerializer
from pilot.tasks.models import TaskGroup
from pilot.workflow.api.api import WorkflowStateViewSet
from pilot.item_types.item_content_fields import get_content_field_specs

from pilot.utils import pilot_languages


def custom_403(request):
    return render(request, '403.html', status=403)


def custom_404(request):
    return render(request, '404.html', status=404)


def custom_500(request):
    return render(request, '500.html', status=500)


def initial_data(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    languages = [{'name': lang[0], 'label': force_text(lang[1])}
                 for lang in request.desk.build_choices_from_allowed_languages()]

    return JsonResponse({
        'user_me': UsersMeViewSet.as_view({'get': 'retrieve'})(request).data,
        'favorites': FavoriteViewSet.as_view({'get': 'list'})(request).data,
        'task_groups': TaskGroupLightSerializer(TaskGroup.objects.filter(desk=request.desk), many=True).data,
        'item_types': ItemTypeViewSet.as_view({'get': 'list'})(request).data,
        'teams': TeamViewSet.as_view({'get': 'list'})(request).data,
        'workflow_states': WorkflowStateViewSet.as_view({'get': 'list'})(request).data,
        'choices': {
            'channels': ChannelViewSet.as_view({'get': 'choices'}, **ChannelViewSet.choices.kwargs)(request).data,
            'languages': languages,
            'projects': ProjectViewSet.as_view({'get': 'choices'}, **ProjectViewSet.choices.kwargs)(request).data,
            'targets': TargetsViewset.as_view({'get': 'choices'}, **TargetsViewset.choices.kwargs)(request).data,
            'users': UsersViewSet.as_view({'get': 'choices'}, **UsersViewSet.choices.kwargs)(request).data,
        },
    })


def languages_choices(request):
    return JsonResponse([
        {
            'value': lang[0],
            'label': str(lang[1])
        }
        for lang in pilot_languages.LANGUAGES_CHOICES
    ], safe=False)


def content_fields_specs(request):
    return JsonResponse(get_content_field_specs(), safe=False)

