from rest_framework import routers

from pilot.tasks.api import api

tasks_api_router = routers.SimpleRouter()
tasks_api_router.register('tasks', api.TaskViewSet, basename='tasks')
tasks_api_router.register('tasks_templates', api.TaskTemplateViewSet, basename='tasks-templates')
tasks_api_router.register('tasks_groups', api.TaskGroupViewSet, basename='tasks-groups')
