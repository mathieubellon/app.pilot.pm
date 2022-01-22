from rest_framework import routers

from pilot.favorites.api import api

favorites_api_router = routers.SimpleRouter()
favorites_api_router.register('favorites', api.FavoriteViewSet, basename='favorites')
