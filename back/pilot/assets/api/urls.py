from rest_framework import routers

from pilot.assets.api import api

assets_api_router = routers.SimpleRouter()
assets_api_router.register('assets', api.AssetViewSet, basename='api-assets')
assets_api_router.register('asset_rights', api.AssetRightViewSet, basename='api-asset-rights')
