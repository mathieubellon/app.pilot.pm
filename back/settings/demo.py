"""Settings for Heroku server : pilotapp-demo."""

from settings.base import *  # noqa
from settings.base import MIDDLEWARE

ON_HEROKU = True
ON_DEMO_SITE = True

# The FQDN protocol to use in emails URLs etc.
FQDN = 'demo.pilot.pm'

# Force SSL accross the site
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') # This is for heroku

ES_ITEM_INDEX = 'items_demo'
ES_PROJECT_INDEX = 'projects_demo'

# Disable outbound emails on the demo site
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


MIDDLEWARE = MIDDLEWARE[:-3] + (
    'pilot.demo.middleware.PilotDemoMiddleware',
) + MIDDLEWARE[-3:]

# Default to english on the demo site
LANGUAGE_CODE = 'en'
