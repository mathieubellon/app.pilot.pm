from django.conf.urls import url

from pilot.main.menu import Menu
from pilot.utils.perms.views import template_view

urlpatterns = [
    url(
        r'^states/$',
        template_view('main_app.html'),
        name='ui_workflow_states'
    ),
]
