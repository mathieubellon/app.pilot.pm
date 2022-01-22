"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
import django
from channels.routing import get_default_application
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.production')
# Flag to differenciate web dyno from worker dyno
os.environ.setdefault('DYNO_TYPE', 'ASGI')

django.setup()
application = SentryAsgiMiddleware(get_default_application())
