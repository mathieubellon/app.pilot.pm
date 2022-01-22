from django.conf.urls import url
from rest_framework import routers

from pilot.utils.api.router import SingleInstanceRouter

from pilot.pilot_users.api import api
from pilot.pilot_users.api import auth_api

users_me_api_router = SingleInstanceRouter()
users_me_api_router.register('users/me', api.UsersMeViewSet, basename='api-users-me')

users_api_router = routers.SimpleRouter()
users_api_router.register('users', api.UsersViewSet, basename='api-users')
users_api_router.register('users_invitations', api.InvitationViewSet, basename='api-usersinvitations')
users_api_router.register('teams', api.TeamViewSet, basename='api-teams')


urlpatterns = [
    url(
        r'^api/notification_preferences/(?P<token>\w+)/$',
        api.UserNotificationPreferenceUpdate.as_view(),
        name='api_notification_preferences'
    ),

    url(
        r'^api/auth/login/$',
        auth_api.LoginApi.as_view(),
        name='api_auth_login'
    ),

    url(
        r'^api/auth/registration/$',
        auth_api.RegistrationApi.as_view(),
        name='api_auth_registration'
    ),

    url(
        r'^api/auth/password/reset/$',
        auth_api.PasswordResetApi.as_view(),
        name='api_auth_password_reset'
    ),

    url(
        r'^api/auth/password/set/$',
        auth_api.PasswordSetApi.as_view(),
        name='api_auth_password_set'
    ),

    url(
        r'^api/auth/invitation/confirm/$',
        auth_api.InvitationConfirmApi.as_view(),
        name='api_auth_invitation_confirm'
    ),
]
