from django.conf.urls import url

from pilot.main.menu import Menu
from pilot.utils.perms.views import template_view
from pilot.sharings import views

urlpatterns = [
    url(
        r'^$',
        template_view('main_app.html'),
        name='ui_sharings_admin'
    ),

    url(
        r'^password/(?P<token>\w+)/$',
        views.sharing_password_required,
        name='ui_sharing_password_required'
    ),

    url(
        r'^(?P<token>\w+)/items/(?P<item_pk>\d+)/$',
        views.sharing,
        name='ui_shared_item'
    ),

    url(
        r'^(?P<token>\w+)/$',
        views.sharing,
        name='ui_sharing'
    ),
]

