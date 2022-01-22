from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.tokens import default_token_generator
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.views import LogoutView, PasswordResetConfirmView, INTERNAL_RESET_SESSION_TOKEN
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from pilot.pilot_users import registration
from pilot.pilot_users.models import PilotUser
from pilot.utils import perms as perms_utils


def auth_app(request, token=None):
    return render(request, "users/auth.html")


@perms_utils.nologin_required
def registration_confirm(request, uidb64=None, token=None):
    """Registration confirmation. The user has clicked on the confirmation link provided in the email."""

    try:
        uid_int = urlsafe_base64_decode(uidb64)
        user = PilotUser.objects.get(id=uid_int)
    except (TypeError, ValueError, OverflowError, PilotUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):

        # Activate the desk and organization of the user which has confirmed his email
        registration.activate_new_desk(user)

        # Log in the user
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        # This will be used to display the onboarding to the user
        request.session[settings.SESSION_FIRST_LOGIN] = True

        # Redirect to the dashboard
        return HttpResponseRedirect('/')

    else:
        raise Http404


class PilotPasswordResetConfirmView(PasswordResetConfirmView):
    def get(self, request, uidb64, token):
        return render(request, "users/auth.html", {
            'uidb64': uidb64,
            'token': self.request.session.get(INTERNAL_RESET_SESSION_TOKEN),
            'invalid_token': not self.validlink
        })


class PilotLogoutView(LogoutView):
    next_page = 'auth_login'

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        response = super(PilotLogoutView, self).dispatch(request, *args, **kwargs)
        # Keep the last desk into the anonymous session
        if request.desk:
            request.session[settings.SESSION_CURRENT_DESK_ID] = request.desk.id
        return response
