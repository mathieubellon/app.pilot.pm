from rest_framework import routers

from pilot.activity_stream.api import api

activity_stream_api_router = routers.SimpleRouter()
activity_stream_api_router.register('activity', api.ActivityViewSet, basename='activity')
