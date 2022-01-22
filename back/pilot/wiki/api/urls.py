from rest_framework import routers
from pilot.wiki.api import api

wiki_api_router = routers.SimpleRouter()
wiki_api_router.register('wiki_pages', api.WikiPageViewset, basename='wiki')

