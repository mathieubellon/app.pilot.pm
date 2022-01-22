from rest_framework import routers
from pilot.integrations.api import api

integrations_api_router = routers.SimpleRouter()
integrations_api_router.register('api_tokens', api.ApiTokenViewset, basename='api-tokens')

