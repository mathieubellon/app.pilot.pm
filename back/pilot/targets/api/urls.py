from rest_framework import routers
from pilot.targets.api import api

targets_api_router = routers.SimpleRouter()
targets_api_router.register('targets', api.TargetsViewset, basename='targets')

