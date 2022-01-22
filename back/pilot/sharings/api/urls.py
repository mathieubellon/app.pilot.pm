from django.conf.urls import url
from rest_framework import routers
from pilot.sharings.api import api

sharings_api_router = routers.SimpleRouter()
sharings_api_router.register('sharings', api.SharingsViewset, basename='api-sharings')

sharings_api_router_shared = routers.SimpleRouter()
sharings_api_router_shared.register('feedbacks', api.SharedItemFeedbackViewset, basename='api-feedbacks')

urlpatterns_shared_item = [
    url(
        r'^items/(?P<pk>\d+)/$',
        api.SharedItemRetrieve.as_view(),
        name='api_shared_item'
    ),
]
