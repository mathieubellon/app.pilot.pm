from rest_framework import routers

from pilot.item_types.api import api

item_types_api_router = routers.SimpleRouter()
item_types_api_router.register('items/types', api.ItemTypeViewSet, basename='api-item-types')
