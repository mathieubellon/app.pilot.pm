import os

import dj_database_url
import sentry_sdk
from django.urls import reverse_lazy
from elasticsearch import Elasticsearch
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.rq import RqIntegration

from pilot.utils.sentry import SENTRY_RELEASE


BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
FRONTEND_ROOT = os.path.join(BACKEND_ROOT, '..', 'front')


def backend_path(*path_parts):
    return os.path.join(BACKEND_ROOT, *path_parts)


def frontend_path(*path_parts):
    return os.path.join(FRONTEND_ROOT, *path_parts)


DEBUG = False
TESTING = False
ON_HEROKU = False
ON_DEMO_SITE = False

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts

ALLOWED_HOSTS = [
    '127.0.0.1',
    '0.0.0.0',
    '.pilot.pm',  # Allow domain and subdomains
    '.pilot.pm.',  # Allow domain and subdomains
    '.herokuapp.com',  # Allow domain and subdomains
    '.herokuapp.com.',  # Also allow FQDN and subdomains
]

SITE_ID = 1

# ----------------------------------------------------------------------------------------------------------------------
# Installed apps
# ----------------------------------------------------------------------------------------------------------------------

DJANGO_APPS = (
    'pilot.apps.DjangoChannelsConfig',
    'django.contrib.admin.apps.AdminConfig',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.messages', # Needed for the django admin
    'django.contrib.postgres',
    'django.contrib.sessions',
    'django.contrib.sites',
    # 'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
)

PILOT_APPS = (
    'pilot.pilot_users.apps.PilotUsersAppConfig',
    'pilot.main',
    'pilot.organizations',
    'pilot.desks',
    'pilot.accounts',
    'pilot.activity_stream.apps.ActivityStreamConfig',
    'pilot.assets',
    'pilot.big_filter',
    'pilot.channels.apps.ChannelAppConfig',
    'pilot.comments.apps.CommentsConfig',
    'pilot.dashboard',
    'pilot.favorites',
    'pilot.item_types',
    'pilot.items',
    'pilot.itemsfilters.apps.CustomItemsUIConfig',
    'pilot.labels.apps.LabelsConfig',
    'pilot.list_config',
    'pilot.messaging',
    'pilot.notifications',
    'pilot.projects',
    'pilot.integrations',
    'pilot.queue.apps.QueueConfig',
    'pilot.search',
    'pilot.sharings',
    'pilot.targets',
    'pilot.tasks',
    'pilot.wiki.apps.WikiConfig',
    'pilot.workflow.apps.WorkflowConfig',

    'pilot.demo',
)

THIRD_PARTY_APPS = (
    'rest_framework',
    'django_filters',
    'storages',
    'impersonate',
    'webpack_loader'
)

INSTALLED_APPS = DJANGO_APPS + PILOT_APPS + THIRD_PARTY_APPS

# -----------
# Middleware
# -----------


MIDDLEWARE = (
    # Whitenoise
    'whitenoise.middleware.WhiteNoiseMiddleware',

    # Django
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware', # Needed for the django admin
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Impersonate
    'impersonate.middleware.ImpersonateMiddleware',

    # Pilot
    'pilot.main.middleware.BundleControlMiddleware',
    'pilot.main.middleware.PilotMiddleware',
    'pilot.main.middleware.UserLogMiddleware',
    'pilot.main.middleware.CacheControlMiddleware',
)

# ----------------------------------------------------------------------------------------------------------------------
# Routing
# ----------------------------------------------------------------------------------------------------------------------

ROOT_URLCONF = 'pilot.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'pilot.wsgi.application'

ASGI_APPLICATION = "pilot.routing.application"


# ----------------------------------------------------------------------------------------------------------------------
# Redis
# ----------------------------------------------------------------------------------------------------------------------

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

# ----------------------------------------------------------------------------------------------------------------------
# Django-channels
# ----------------------------------------------------------------------------------------------------------------------

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [REDIS_URL],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}

# ----------------------------------------------------------------------------------------------------------------------
# Templates
# ----------------------------------------------------------------------------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            backend_path('templates/'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Django
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages', # Needed for the django admin

                # Pilot.
                'pilot.main.context_processors.pilot_context',
            ],
        },
    },
]

# ----------------------------------------------------------------------------------------------------------------------
# Locale
# ----------------------------------------------------------------------------------------------------------------------

gettext = lambda s : s

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html

LANGUAGES = (
    ('fr', gettext('Français')),
    ('en', gettext('Anglais')),
)

LANGUAGE_CODE = 'fr'

LOCALE_PATHS = (
    backend_path('locale'),
)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

DATE_FORMAT = 'd b Y'

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True


# ----------------------------------------------------------------------------------------------------------------------
# Session.
# ----------------------------------------------------------------------------------------------------------------------

# Session expires on browser close (unless user check "Remember me" when user logs in)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# When the user check "Remember me", we use a veeeeeery long session duration
SESSION_COOKIE_AGE = 80 * 365 * 24 * 60 * 60  # 80 years. We're in 2020... will pilot still be there by 2100 ? ;-)
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'


# ----------------------------------------------------------------------------------------------------------------------
# Django contrib auth app.
# ----------------------------------------------------------------------------------------------------------------------

AUTH_USER_MODEL = 'pilot_users.PilotUser'
LOGIN_URL = reverse_lazy('auth_login')
LOGIN_REDIRECT_URL = reverse_lazy('dashboard')

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ----------------------------------------------------------------------------------------------------------------------
# Pilot settings.
# ----------------------------------------------------------------------------------------------------------------------

SECRET_KEY = os.environ.get('SECRET_KEY')  # Raises ImproperlyConfigured exception if SECRET_KEY not found

# The HTTP protocol to use in emails URLs etc.
HTTP_PROTOCOL = 'https'

# ----------------------------------------------------------------------------------------------------------------------
# Databases
# ----------------------------------------------------------------------------------------------------------------------

DATABASE_URL = os.environ.get('DATABASE_URL', "postgres://admin:admin@localhost:5432/pilotdevdb")
CONN_MAX_AGE = os.environ.get('CONN_MAX_AGE', 0)

DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}

# Set this to True to wrap each HTTP request in a transaction on this database.
ATOMIC_REQUESTS = True

# ----------------------------------------------------------------------------------------------------------------------
# Cache
# ----------------------------------------------------------------------------------------------------------------------

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# ----------------------------------------------------------------------------------------------------------------------
# Email
# ----------------------------------------------------------------------------------------------------------------------

EMAIL_BACKEND = 'postmark.django_backend.EmailBackend'
DEFAULT_FROM_EMAIL = 'hello@pilot.pm'
EMAIL_INBOUND_SERVER = os.environ.get('EMAIL_INBOUND_SERVER')

# In production emails are routed by https://postmarkapp.com
POSTMARK_API_KEY = os.environ.get('POSTMARK_API_KEY')
POSTMARK_SENDER = 'hello@pilot.pm'
POSTMARK_TEST_MODE = False

# ----------------------------------------------------------------------------------------------------------------------
# File Upload
# ----------------------------------------------------------------------------------------------------------------------

# The default value is 2.5MB, but this is too low for the postmark inbound webhook.
# Increase it to prevent errors on postmark_inbound_webhook()
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 10

# ----------------------------------------------------------------------------------------------------------------------
# Pilot session keys.
# ----------------------------------------------------------------------------------------------------------------------

# Is it the first login ? (will trigger onboarding tour)
SESSION_FIRST_LOGIN = 'first_login'

# Desk currently connected at
SESSION_CURRENT_DESK_ID = 'current_desk_id'

# Boolean. True if a password has been checked before seeing a shared Item. False otherwise.
SHARING_PASSWORD_CHECKED = 'sharing_password_checked'

# ----------------------------------------------------------------------------------------------------------------------
# MEDIA FILES
# Directly uploaded to and served by AWS S3 only at the moment
# Todo : Make it work with FileSystemStorage
# ----------------------------------------------------------------------------------------------------------------------

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Amazon S3 storage.

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_REGION = os.environ.get('AWS_REGION')
AWS_S3_REGION_NAME = AWS_REGION # This is for S3Boto3Storage
AWS_QUERYSTRING_AUTH = False
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_PRELOAD_METADATA = True
S3_USE_SIGV4 = True
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
EMBED_THUMB_WIDTH = 450
PREVIEW_THUMB_WIDTH = 150
AWS_DEFAULT_ACL = 'public-read'

if AWS_STORAGE_BUCKET_NAME:
    # AWS_S3_ENDPOINT = "%s.pilot.pm" % AWS_STORAGE_BUCKET_NAME
    AWS_S3_ENDPOINT = "%s.s3.amazonaws.com" % AWS_STORAGE_BUCKET_NAME
    AWS_S3_BASE_URL = "https://%s/" % AWS_S3_ENDPOINT

else:
    AWS_S3_ENDPOINT = None
    AWS_S3_BASE_URL = None

# Key to use during demo asset copy. It should have access to both the production bucket and the demo bucket
DEMO_COPY_AWS_ACCESS_KEY_ID = os.environ.get('DEMO_COPY_AWS_ACCESS_KEY_ID')
DEMO_COPY_AWS_SECRET_ACCESS_KEY = os.environ.get('DEMO_COPY_AWS_SECRET_ACCESS_KEY')

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
# We do not use them at the moment but we leave this setting in case FileSystemStorage is activated
MEDIA_ROOT = backend_path('media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# ----------------------
# Media files conversions : by https://transloadit.com
# ----------------------

TRANSLOADIT = True
TRANSLOADIT_AUTH_KEY = os.environ.get('TRANSLOADIT_AUTH_KEY')
TRANSLOADIT_AUTH_SECRET = os.environ.get('TRANSLOADIT_AUTH_SECRET')

# ----------------------------------------------------------------------------------------------------------------------
# STATIC FILES
# ----------------------------------------------------------------------------------------------------------------------

# We use Whitenoise to compress (gzip) static files
# Their middleware is inherited from Django ManifestStaticFileStorage
# https://docs.djangoproject.com/fr/1.9/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

WHITENOISE_MAX_AGE = 86400

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = backend_path('static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    frontend_path('public'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
    # other finders..
)

# ----------------------
# Static Files builder : Webpack.js
# Django Webpack Loader eads webpack-stats.json ton inject in template last compiled hashed js / css files
# ----------------------


WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': '',
        'STATS_FILE': frontend_path('webpack-stats.json'),
        'POLL_INTERVAL': 0.1
    }
}

# ----------------------------------------------------------------------------------------------------------------------
# Django Rest Framework.
# ----------------------------------------------------------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'pilot.utils.api.authentication.PilotSessionAuthentication',
    ),
}

# ----------------------------------------------------------------------------------------------------------------------
# Stripe
# ----------------------------------------------------------------------------------------------------------------------

STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')

# ----------------------------------------------------------------------------------------------------------------------
# Sentry
# ----------------------------------------------------------------------------------------------------------------------

SENTRY_BACKEND_DSN = os.environ.get('SENTRY_BACKEND_DSN', '')
SENTRY_WORKER_DSN = os.environ.get('SENTRY_WORKER_DSN', '')
SENTRY_FRONTEND_DSN = os.environ.get('SENTRY_FRONTEND_DSN', '')

if SENTRY_BACKEND_DSN and os.environ.get('DYNO_TYPE') != 'WORKER':

    sentry_sdk.init(
        dsn=SENTRY_BACKEND_DSN,
        integrations=[
            DjangoIntegration(),
            RqIntegration(),
            RedisIntegration()
        ],
        send_default_pii=True,
        release=SENTRY_RELEASE,
        traces_sample_rate=0.2
    )


# ----------------------------------------------------------------------------------------------------------------------
# https://dev.facebook.com
# ----------------------------------------------------------------------------------------------------------------------

FACEBOOK_AUTH_KEY = os.environ.get('FACEBOOK_AUTH_KEY')
FACEBOOK_AUTH_SECRET = os.environ.get('FACEBOOK_AUTH_SECRET')
FACEBOOK_AUTHORIZE_URL = "https://graph.facebook.com/oauth/authorize?"
FACEBOOK_TOKEN_URL = "https://graph.facebook.com/oauth/access_token?"
FACEBOOK_MAX_LENGTH = 10000

# ----------------------------------------------------------------------------------------------------------------------
# twitter.com
# ----------------------------------------------------------------------------------------------------------------------

TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')
TWITTER_MAX_LENGTH = 280

# ----------------------------------------------------------------------------------------------------------------------
# intercom.io
# ----------------------------------------------------------------------------------------------------------------------

INTERCOM_APP_ID = os.environ.get('INTERCOM_APP_ID')
INTERCOM_API_SECRET = os.environ.get('INTERCOM_API_SECRET')

# ----------------------------------------------------------------------------------------------------------------------
# Google Tag Manager
# ----------------------------------------------------------------------------------------------------------------------

GOOGLE_TAG_MANAGER_ID = None

# ----------------------------------------------------------------------------------------------------------------------
# Elasticsearch.
# ----------------------------------------------------------------------------------------------------------------------

ES_DISABLED = False

ES_SERVER = os.environ.get('FOUNDELASTICSEARCH_URL', 'http://localhost:9200')
ES_ITEM_INDEX = 'items'
ES_PROJECT_INDEX = 'projects'
ES_CLIENT = Elasticsearch(ES_SERVER)

# ----------------------------------------------------------------------------------------------------------------------
# Django impersonate.
# ----------------------------------------------------------------------------------------------------------------------

IMPERSONATE = {
    'USE_HTTP_REFERER': True
}

# ----------------------------------------------------------------------------------------------------------------------
# Logging.
# ----------------------------------------------------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s][%(levelname)s][%(name)s][%(funcName)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },

    },
    'loggers': {
        # root logger, as a fallback
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'pilot': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'elasticsearch': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'urllib3': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'django.db.backends': {
            'handlers': ['null'],  # Quiet by default!
            'propagate': False,
            'level': 'DEBUG',
        },
    },
}
