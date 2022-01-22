from django.conf.urls import url

from pilot.dashboard import views

urlpatterns = [
    url(
        r'^$',
        views.dashboard,
        name='dashboard'
    ),

    url(
        r'^(?P<tab>dashboard|notifications|tasks|favorites|search)$',
        views.dashboard,
        name='dashboard_tab'
    ),
]
