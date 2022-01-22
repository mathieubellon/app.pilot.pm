from django.conf.urls import url

from pilot.main.menu import Menu
from pilot.utils.perms.views import template_view

urlpatterns = [
    # Don't add a $ at the end of the regex, so we catch all and let the Vue router decide
    url(
        r'^groups',
        template_view('main_app.html'),
        name='ui_task_group_admin'
    ),
]
