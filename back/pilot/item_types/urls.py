from django.conf.urls import url
from pilot.utils.perms.views import template_view

urlpatterns = [

    # List Item Types
    url(
        r'^$',
        template_view('main_app.html'),
        name='ui_item_types_list'
    ),

    # Edit Item Types
    url(
        r'^(?P<item_type_pk>\d+)/$',
        template_view('main_app.html'),
        name='ui_item_types_edit'
    )
]

