from django.conf.urls import url

from pilot.projects import views


urlpatterns = [
    # Vue.js ProjectApp pages
    # Don't append trailing slash on views managed by Vue router
    # Don't add a $ at the end of the regex, so we catch all and let the Vue router decide which panel he should open
    url(
        r'^$', views.projects_app,
        name='ui_projects_list'
    ),
    url(
        r'^(?P<tab>idea|active|closed)',
        views.projects_app,
        name='ui_projects_list_tab'
    ),
    url(
        r'^(?P<project_pk>\d+)',
        views.projects_app,
        name='ui_project_detail'
    ),
]
