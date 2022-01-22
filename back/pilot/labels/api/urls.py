from rest_framework import routers

from pilot.labels.api import api

labels_api_router = routers.SimpleRouter()
labels_api_router.register('labels', api.LabelViewSet, basename='labels')
