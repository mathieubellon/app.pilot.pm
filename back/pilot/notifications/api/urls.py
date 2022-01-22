from rest_framework import routers

from pilot.notifications.api import api

notifications_api_router = routers.SimpleRouter()
notifications_api_router.register('notifications', api.NotificationViewSet, basename='notifications')
notifications_api_router.register('notification_feeds', api.NotificationFeedViewSet, basename='notification_feeds')
notifications_api_router.register('reminders', api.ReminderViewSet, basename='reminders')
