from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import login as auth_login

from pilot.pilot_users.models import UserInDesk, PERMISSION_ADMINS

# DOn't use settings.FQDN as it could be changed to app.pilot.pm to bypass the check
DEMO_FQDN = 'demo.pilot.pm'


class PilotDemoMiddleware(object):
    """
    Auto-log any incoming request as the first user
    """
    def __init__(self, get_response):
        if not settings.ON_DEMO_SITE:
            raise ImproperlyConfigured("The PilotDemoMiddleware should only be used on the demo site")

        self.get_response = get_response

    def __call__(self, request):
        if not settings.ON_DEMO_SITE:
            raise Exception("Cannot use PilotDemoMiddleware if ON_DEMO_SITE is False")

        host = request.META['HTTP_HOST']
        if not settings.DEBUG and host != DEMO_FQDN:
            raise Exception('Cannot use PilotDemoMiddleware if host is not "{}"'.format(DEMO_FQDN))

        if request.user.is_anonymous:
            # Auto-log the first "real" user ( not user 1 )
            target_user = UserInDesk.objects.exclude(id=1).order_by('id').first().user
            if target_user:
                request.session[settings.SESSION_FIRST_LOGIN] = True
                auth_login(request, target_user, backend='django.contrib.auth.backends.ModelBackend')

        return self.get_response(request)
