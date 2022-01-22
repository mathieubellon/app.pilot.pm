from django.conf.urls import url

from pilot.items.api import api

from rest_framework import routers

items_api_router = routers.SimpleRouter()
items_api_router.register('items', api.ItemViewSet, basename='api-items')

items_api_router_shared = routers.SimpleRouter()
items_api_router_shared.register('items', api.SharedItemViewSet, basename='api-items-shared')

urlpatterns = [
    # List EditSession API
    url(
        r'^(?P<item_pk>\d+)/sessions/$',
        api.EditSessionList.as_view(),
        name='api_sessions_list'
    ),

    # Single EditSession API
    url(
        r'^(?P<item_pk>\d+)/sessions/(?P<pk>\d+)/$',
        api.EditSessionRetrieve.as_view(),
        name='api_session_detail'
    )
]
