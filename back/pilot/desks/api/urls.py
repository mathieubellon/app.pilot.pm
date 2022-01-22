from rest_framework import routers
from pilot.desks.api import api

desks_api_router = routers.SimpleRouter()
desks_api_router.register('desks', api.DeskViewset, basename='desks')

export_api_router = routers.SimpleRouter()
export_api_router.register('exports', api.ExportViewset, basename='exports')
