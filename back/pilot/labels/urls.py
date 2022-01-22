from django.conf.urls import url

from pilot.main.menu import Menu
from pilot.utils.perms.views import template_view

urlpatterns = [
    url(
        r'^',
        template_view('main_app.html'),
        name='ui_labels_list'
    ),
]
