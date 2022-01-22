"""Settings for tests."""

import os
from settings.base import *  # noqa

DEBUG = False
TESTING = True

# The FQDN protocol to use in emails URLs etc.
FQDN = os.environ.get('FQDN')

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ALLOWED_HOSTS = ['*']

WEBPACK_LOADER['DEFAULT']['CACHE'] = False
WEBPACK_LOADER['DEFAULT']['STATS_FILE'] = frontend_path('webpack-stats.json')

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Do not force cookie to be transported through SSL connexion
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = '0.0.0.0:8082'

TEMPLATE_DEBUG = False

# Override and remove useless middleware classes (locale) that slow down tests.
# Also remove whitenoise from the middleware, so we can explicitely serve the statics with django
MIDDLEWARE = (
    # Django
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Pilot
    'pilot.main.middleware.PilotMiddleware',
    'pilot.main.middleware.UserLogMiddleware',

)

PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)

TEMPLATES[0]['APP_DIRS'] = False
TEMPLATES[0]['OPTIONS']['loaders'] = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

# Do not try to connect to the ElasticSearch service during the tests
ES_DISABLED = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
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
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
            'formatter': 'simple'
        },
        'console.watchdog': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
            'formatter': 'verbose'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },

    },
    'loggers': {
        'factory': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'CRITICAL',
        },
        'boto': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'CRITICAL',
        },
        'PIL': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'CRITICAL',
        },
        'pilot': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'CRITICAL',
        },
        'elasticsearch': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'CRITICAL',
        },
        'urllib3': {
            'handlers': ['null'],
            'propagate': False,
            'level': 'CRITICAL',
        },
        'selenium': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'CRITICAL',
        },
        'django.db.backends': {
            'handlers': ['null'],  # Quiet by default!
            'propagate': False,
            'level': 'CRITICAL',
        },

    },
}
