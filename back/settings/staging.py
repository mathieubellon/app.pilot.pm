"""Settings for Heroku server : pilotapp-staging."""

from settings.base import *  # noqa

ON_HEROKU = True

# The FQDN protocol to use in emails URLs etc.
FQDN = 'staging.pilot.pm'

# Force SSL accross the site
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') # This is for heroku

ES_ITEM_INDEX = 'items_staging'
ES_PROJECT_INDEX = 'projects_staging'
