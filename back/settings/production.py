"""Settings for Heroku server : pilotapp-production-master."""

from settings.base import *  # noqa

ON_HEROKU = True

# The FQDN protocol to use in emails URLs etc.
FQDN = 'app.pilot.pm'

# Force SSL accross the site
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # This is for heroku

# Deactivate HTML rendering on production
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',)
})

GOOGLE_TAG_MANAGER_ID = 'GTM-M7KJ6QP'
