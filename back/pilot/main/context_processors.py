import hmac
import hashlib

from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from pilot.accounts.usage_limit import get_all_usage_limits
from pilot.assets.models import Asset
from pilot.channels.models import Channel
from pilot.items.models import Item
from pilot.main.menu import LOGIN_MENU_CHOICES
from pilot.projects.models import Project
from pilot.utils import pilot_languages, pilot_timezones
from pilot.utils.html import get_webpack_bundle_name, render_json
from pilot.utils.sentry import SENTRY_RELEASE
from pilot.wiki.models import WikiPage


def pilot_context(request):
    """Custom template context processor to push settings variables in templates."""
    content_types = {}
    models = (
        Asset,
        Channel,
        Item,
        Project,
        WikiPage,
    )

    for model in models:
        content_type = ContentType.objects.get_for_model(model)
        content_types[model.__name__] = {
            'id': content_type.id,
            'name': content_type.name,
            'modelName': model.__name__
        }

    usage_limits = get_all_usage_limits(request.desk) if request.desk else []
    usage_limits = {limit['name']: limit for limit in usage_limits}

    ui_languages = [{'value': lang[0], 'label': lang[1]} for lang in pilot_languages.PILOT_UI_LANGUAGES]
    timezones = [{'value': timezone.name, 'label': timezone.label} for timezone in pilot_timezones.timezones]
    login_menus = [{'value': menu[0], 'label': menu[1]} for menu in LOGIN_MENU_CHOICES]

    intercom_user_hash = None
    if request.user.is_authenticated and settings.INTERCOM_API_SECRET:
        intercom_user_hash = hmac.new(
            settings.INTERCOM_API_SECRET.encode(),
            request.user.email.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

    return {
        'pilot_context': {
            'content_types': content_types,
            # Pop first_login value, so the tour won't trigger in the next pages
            'first_login': request.session.pop(settings.SESSION_FIRST_LOGIN, False),
            'intercom_enabled': settings.INTERCOM_APP_ID and not settings.DEBUG,
            'intercom_user_hash': intercom_user_hash,
            'login_menus': render_json(login_menus),
            'on_demo_site': settings.ON_DEMO_SITE,
            'sentry_frontend_enabled': bool(settings.SENTRY_FRONTEND_DSN) and not settings.DEBUG,
            'sentry_release': SENTRY_RELEASE,
            'timezones': timezones,
            'ui_languages': render_json(ui_languages),
            'usage_limits': render_json(usage_limits),
            'bundle_name': get_webpack_bundle_name(),
            'settings': {
                'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
                'AWS_S3_BASE_URL': settings.AWS_S3_BASE_URL,
                'SENTRY_FRONTEND_DSN': settings.SENTRY_FRONTEND_DSN,
                'INTERCOM_APP_ID': settings.INTERCOM_APP_ID,
                'GOOGLE_TAG_MANAGER_ID': settings.GOOGLE_TAG_MANAGER_ID
            }
        },

    }
