from django.conf.urls import url
from django.urls import re_path
from django.views.generic import RedirectView

from pilot.items import views

urlpatterns = [
    # Vue.js ItemApp pages
    # Don't append trailing slash on views managed by Vue router
    # Don't add a $ at the end of the regex, so we catch all and let the Vue router decide which panel he should open
    url(
        r'^$',
        views.items_app,
        name='ui_items_list'
    ),
    # Item list
    url(
        r'^(?P<tab>active|trash)',
        views.items_app,
        name='ui_items_list_tab'
    ),
    url(
        r'^filter/(?P<saved_filter_pk>\d+)',
        views.items_app,
        name='ui_saved_filter_list'
    ),
    # Item calendar
    url(
        r'^calendar/filter/(?P<saved_filter_pk>\d+)$',
        views.items_app,
        name='ui_saved_filter_calendar'
    ),
    url(
        r'^calendar',
        views.items_app,
        name='ui_main_calendar'
    ),
    # View an item.
    url(
        r'^(?P<item_pk>\d+)$',
        views.items_app,
        name='ui_item_details'
    ),


    # Export an item.
    url(
        r'^(?P<item_pk>\d+)/export/$',
        views.item_export,
        name='ui_item_export'
    ),

    # View an old version of an item
    # Not used anymore, but some old url may still persist in some user's mailbox.
    # Redirect to the main item view
    url(
        r'^(?P<item_pk>\d+)/version/(\d+)/$',
        RedirectView.as_view(pattern_name='ui_item_details', permanent=False, query_string=True)
    ),


    # LEGACY REVIEW URL kept to redirect to the new ones
    re_path(r'^review/(?P<tail>.*)$', RedirectView.as_view(url='/sharings/%(tail)s', query_string=True)),
]

