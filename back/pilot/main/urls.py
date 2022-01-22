from django.conf.urls import url

from pilot.main import views

urlpatterns = [
    url(
        r'^api/initial/$',
        views.initial_data,
        name='api_init'
    ),

    url(
        r'^api/languages/$',
        views.languages_choices,
        name='choices_aggregate'
    ),

    url(
        r'^api/contentFieldsSpecs/$',
        views.content_fields_specs,
        name='content_fields_specs'
    ),

    url(r'^403/$', views.custom_403, name='403'),
    url(r'^404/$', views.custom_404, name='404'),
    url(r'^500/$', views.custom_500, name='500')
]
