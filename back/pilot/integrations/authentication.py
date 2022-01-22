from django.contrib.auth.models import AnonymousUser
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import BasePermission

from pilot.integrations.models import ApiToken


class ApiTokenAuthentication(TokenAuthentication):
    """
    Ensure that the API Token exists.
    """

    def authenticate_credentials(self, token):
        try:
            token = ApiToken.objects.get(token=token)
        except ApiToken.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        return (AnonymousUser(), token)


class HasApiToken(BasePermission):
    """
    Allows access only to users with a correct token.
    Use this with ApiTokenAuthentication.
    This permission check will also set request.desk
    """

    def has_permission(self, request, view):
        if request.auth:
            request.desk = request.auth.desk
            return True
        else:
            return False
