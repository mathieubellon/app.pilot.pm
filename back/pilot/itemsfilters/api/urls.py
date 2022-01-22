from rest_framework import routers

from pilot.itemsfilters.api import api

item_filters_api_router = routers.SimpleRouter()

item_filters_api_router.register(
    'saved_filters',
    api.SavedFilterViewSet,
    basename='saved_filter'
)
item_filters_api_router.register(
    'internal_shared_filters',
    api.InternalSharedFilterViewSet,
    basename='internal_shared_filter'
)
