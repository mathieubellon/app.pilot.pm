from rest_framework import routers

from pilot.channels.api import api

channels_api_router = routers.SimpleRouter()
channels_api_router.register('channels', api.ChannelViewSet, basename='api-channels')
