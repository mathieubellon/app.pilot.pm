from rest_framework import routers
from pilot.utils.api.router import SingleInstanceRouter
from pilot.accounts.api import api


account_api_router = SingleInstanceRouter()
account_api_router.register('subscription', api.SubscriptionViewset, basename='subscription')

plans_api_router = routers.SimpleRouter()
plans_api_router.register('plans', api.SubscriptionPlanViewSet, basename='plans')
