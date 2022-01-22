from rest_framework import routers

from pilot.list_config.api import api

list_config_api_router = routers.SimpleRouter()
list_config_api_router.register('list_config', api.ListConfigViewSet, basename='api-list-config')

list_config_api_router_shared = routers.SimpleRouter()
list_config_api_router_shared.register('list_config', api.SharedListConfigViewSet, basename='api-list-config-shared')
