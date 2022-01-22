import collections
import json
import logging

from django.conf import settings
from django.http import HttpResponse
from ipware.ip import get_ip

from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout as auth_logout

from pilot.desks.utils import connect_to_desk, get_current_desk
from pilot.queue.jobs import Job
from pilot.utils import pilot_languages
from pilot.utils.html import get_webpack_bundle_name


class PilotMiddleware(MiddlewareMixin):
    """
    Store the currently used organization and desk on the request object (as for request.user) :
     - request.desk
     - request.organization

    If the user is anonymous, or not associated with a desk, then the attributes are set to None.

    Also handle Job Queue cleanup
    """

    def try_activate_lang_from_query(self, request):
        if 'lang' in request.GET:
            lang = pilot_languages.validate_user_language(request.GET['lang'])
            request.session[translation.LANGUAGE_SESSION_KEY] = lang
            translation.activate(lang)

    def try_connect_user(self, request):
        desk = get_current_desk(request.user, request.session)
        if desk:
            connect_to_desk(desk, request)
        elif not request.user.is_impersonate and not request.user.is_superuser:
            # If the user is not linked to any desk, we should logout him
            request.session.pop(settings.SESSION_CURRENT_DESK_ID, None)
            auth_logout(request)

    def process_request(self, request):
        # Default to None for anonymous users
        request.desk = None
        request.organization = None

        if settings.ON_DEMO_SITE:
            # On the demo site, don't use the user language preference,
            # just use the session as if it were an anonymous user
            self.try_activate_lang_from_query(request)

            # Now we can connect him
            self.try_connect_user(request)

        elif request.user.is_authenticated:
            # Language is associated to authenticated users.
            # Override the language selected by LocaleMiddleware.
            # But only if we're running normal application.
            # On the demo site, the lang parameter take precedence.
            translation.activate(request.user.language)

            self.try_connect_user(request)

        else:
            # On the main site,
            # check the query params to activate a language for anonymous users
            self.try_activate_lang_from_query(request)

        # Anonymous users can toggle (fr/en) page translation
        # The set_language view provided by django provide the logic to update language key in session
        # Then the LocaleMiddleware will take care of setting the correct language
        # If no langauge is specified, LocaleMiddleware will try the Accept-Language Header
        # And will finally fall back to settings.LANGUAGE_CODE ('fr' currently)
        # We have nothing to do ourselve here
        # https://docs.djangoproject.com/en/1.11/topics/i18n/translation/#how-django-discovers-language-preference

        # Reset Job Queue thread local pending jobs for the new request
        Job.reset_pending_jobs()


class BundleControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        client_bundle_name = request.headers.get('Bundle-Name')
        if client_bundle_name:
            current_bundle_name = get_webpack_bundle_name()
            # The client bundle is outdated, he need to reload, send a header accordingly
            if current_bundle_name != client_bundle_name:
                # status 419 is a custom, non-assigned http response code
                return HttpResponse(status=419)

        return self.get_response(request)


class CacheControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Tell the browser to never cache API calls
        if request.path.startswith('/api'):
            response['Cache-Control'] = 'no-store'
        return response


class UserLogMiddleware(MiddlewareMixin):
    """
    Log user behavior
    """

    def process_response(self, request, response):
        payload = collections.OrderedDict()
        payload['method'] = getattr(request, 'method', '')
        payload['path'] = getattr(request, 'path', '')
        # We don't log request.POST anymore, because this is used on html forms, and we only use the API now

        if hasattr(request, 'user') and request.user.is_authenticated:
            payload['userid'] = getattr(request.user, 'id', '')

            try:
                payload['deskid'] = request.desk.id
            except Exception:
                pass

            try:
                payload['ip'] = get_ip(request)
            except Exception:
                pass

            logging.getLogger('pilot.userlog').info(json.dumps(payload))

        else:
            logging.getLogger('pilot.anonymoususerlog').info(json.dumps(payload))

        return response
