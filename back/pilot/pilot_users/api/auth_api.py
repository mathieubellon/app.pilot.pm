from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import INTERNAL_RESET_SESSION_TOKEN
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.conf import settings
from django.shortcuts import resolve_url
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.db import transaction
from django.http import HttpResponseRedirect

from rest_framework import views
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from pilot.main.menu import MENU_ELEMENTS_DICT
from pilot.utils.api import sensitive_post_parameters_m, never_cache_m
from pilot.pilot_users.api.auth_serializers import LoginSerializer, PasswordSetSerializer, RegistrationSerializer, \
    InvitationConfirmSerializer
from pilot.pilot_users.models import PilotUser, InvitationToken
from pilot.pilot_users import registration
from pilot.notifications import emailing
from pilot.accounts.subscription import update_stripe_subscription_items
from pilot.accounts.usage_limit import UserUsageLimit
from pilot.activity_stream.models import Activity
from pilot.activity_stream.jobs import create_activity
from pilot.desks.utils import connect_to_desk


class LoginApi(views.APIView):

    @sensitive_post_parameters_m
    @never_cache_m
    def dispatch(self, *args, **kwargs):
        return super(LoginApi, self).dispatch(*args, **kwargs)

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        remember_me = serializer.data.get('remember_me')
        next_url = serializer.data.get('next')

        auth_login(self.request, user)

        # If the remember_me checkbox is checked, the user won't be logged out on browser close.
        # Instead, it will remain logged in until the cookie expires
        if remember_me:
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)

        return Response({'redirect': self.get_success_url(next_url)})

    def get_success_url(self, next_url):
        user = self.request.user

        next_url_is_safe = is_safe_url(
            url=next_url,
            allowed_hosts=[self.request.get_host()],
            require_https=self.request.is_secure(),
        )
        if next_url_is_safe and next_url != '/':
            return next_url
        elif user.is_authenticated:
            return resolve_url(MENU_ELEMENTS_DICT[user.login_menu].home_view)
        else:
            return resolve_url(settings.LOGIN_REDIRECT_URL)


class RegistrationApi(views.APIView):
    """Generates a one-use only link for resetting password and sends to the user."""

    @sensitive_post_parameters_m
    @never_cache_m
    def dispatch(self, *args, **kwargs):
        return super(RegistrationApi, self).dispatch(*args, **kwargs)

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)

        registration.create_new_desk(request, serializer.data)
        return Response()


class PasswordResetApi(views.APIView):
    """Generates a one-use only link for resetting password and sends to the user."""

    def post(self, request):
        email = request.data.get('email', '').strip()
        users = PilotUser.objects.filter(email__iexact=email)

        for user in users:
            emailing.send_password_reset(user)

        return Response()


class PasswordSetApi(views.APIView):
    """An API that lets a user change set their password without entering the old password"""

    @sensitive_post_parameters_m
    @never_cache_m
    def dispatch(self, *args, **kwargs):
        return super(PasswordSetApi, self).dispatch(*args, **kwargs)

    def post(self, request):
        uidb64 = request.data.get('uidb64')
        user = self.get_user(uidb64)

        session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
        if not default_token_generator.check_token(user, session_token):
            return HttpResponseForbidden()

        serializer = PasswordSetSerializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)

        password1 = serializer.data.get('password1')
        user.set_password(password1)
        user.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        return Response()

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = PilotUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, PilotUser.DoesNotExist, ValidationError):
            user = None
        return user


class InvitationConfirmApi(views.APIView):
    """Confirm an invitation token and create a new Pilot user."""

    @sensitive_post_parameters_m
    @never_cache_m
    def dispatch(self, *args, **kwargs):
        return super(InvitationConfirmApi, self).dispatch(*args, **kwargs)

    def initial(self, request, *args, **kwargs):
        token = request.data.get('token', request.query_params.get('token'))

        self.invitation_token = None
        self.existing_user = None
        self.different_user_connected = False

        try:
            self.invitation_token = InvitationToken.objects.get(token=token)

            # Handle the case where a user is already connected, and he receive an invitation on another email
            self.different_user_connected = (
                request.user.is_authenticated and
                self.invitation_token.email.lower() != request.user.email.lower()
            )

            self.existing_user = PilotUser.objects.get(email=self.invitation_token.email)
        except ObjectDoesNotExist:
            pass

    def get(self, request):
        if not self.invitation_token:
            return Response({'invalid_token': True})

        if self.invitation_token.used:
            return Response({'used_token': True})

        context = {
            'desk_name': self.invitation_token.desk.name,
            'existing_user_name': self.existing_user.get_short_name() if self.existing_user else None,
            'inviter': self.invitation_token.created_by.get_friendly_name(),
            'invitation_email': self.invitation_token.email
        }

        # Handle the case where a user is already connected, and he receive an invitation on another email
        if self.different_user_connected:
            context.update({
                'current_email': request.user.email,
                'different_user_connected': True,
            })

        return Response(context)

    def post(self, request):
        if not self.invitation_token or self.invitation_token.used:
            return HttpResponseBadRequest()

        desk = self.invitation_token.desk

        with transaction.atomic():
            # Ensure the desk has enough user usage available before creating/associating the new user
            UserUsageLimit(self.invitation_token.desk).check_limit(allow_exact_limit=True)

            if self.different_user_connected:
                auth_logout(request)

            if self.existing_user:
                joined_user = registration.associate_invited_user_to_desk(self.existing_user, self.invitation_token)
            else:
                serializer = InvitationConfirmSerializer(data=request.data, context={'user': request.user})
                serializer.is_valid(raise_exception=True)
                joined_user = registration.create_invited_user(request, serializer.data, self.invitation_token)
                request.session[settings.SESSION_FIRST_LOGIN] = True

            # When there's a new user, we need to update the billing amount
            update_stripe_subscription_items(desk.organization)

            if request.user.is_authenticated:
                # If the user is already authenticated, he is on another desk, we must reconnect him on the new desk
                connect_to_desk(desk, request)
            else:
                # Auto-login
                auth_login(request, joined_user, backend='django.contrib.auth.backends.ModelBackend')

            create_activity(
                actor=joined_user,
                desk=desk,
                verb=Activity.VERB_JOINED_TEAM,
                target=desk
            )

            return HttpResponseRedirect('/')
