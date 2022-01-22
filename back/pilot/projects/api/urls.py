from django.conf.urls import url

from pilot.projects.api import api

from rest_framework import routers

projects_api_router = routers.SimpleRouter()
projects_api_router.register('projects', api.ProjectViewSet, basename='api-projects')

urlpatterns = [
    url(
        r'^calendar/$',
        api.CalendarProjectListView.as_view(),
        name='api_calendar_projects_list'
    ),
]

urlpatterns_shared_project = [
    url(
        r'^projects/calendar/$',
        api.SharedCalendarProjectList.as_view(),
        name='api_shared_calendar_projects_list'
    ),
]


