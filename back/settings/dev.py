"""Base settings for development."""
from settings.base import *  # noqa

DEBUG = True

# INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
# MIDDLEWARE = MIDDLEWARE + ('debug_toolbar.middleware.DebugToolbarMiddleware',)

INSTALLED_APPS = INSTALLED_APPS + ('drf_yasg', )

HTTP_PROTOCOL = "http"
# The FQDN protocol to use in emails URLs etc.
FQDN = os.environ.get('FQDN', 'http://0.0.0.0:8000')

INTERNAL_IPS = ('127.0.0.1', '0.0.0.0')

# Do not force cookie to be transported through SSL connexion
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Do not redirect to https in dev
SECURE_SSL_REDIRECT = False

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Uncomment for transactionnal email testing
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# DEFAULT_FROM_EMAIL = 'hello@pilot.pm'

# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'xxxxxxxx'
# EMAIL_HOST_PASSWORD = 'xxxxxx'
# EMAIL_PORT = 587

ALLOWED_HOSTS = ['*']


WEBPACK_LOADER['DEFAULT']['CACHE'] = False
WEBPACK_LOADER['DEFAULT']['STATS_FILE'] = frontend_path('webpack-stats-dev.json')


# DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

ES_URL = 'localhost'
ES_DISABLED = False

SWAGGER_SETTINGS = {
   'DEFAULT_AUTO_SCHEMA_CLASS': 'doc.open_api.APISwaggerAutoSchema',
}


# Adapt logging to dev env
LOGGING['handlers']['console']['formatter'] = 'simple'
LOGGING['loggers']['pilot']['level'] = 'ERROR'
LOGGING['loggers']['urllib3']['handlers'] = ['console']
LOGGING['loggers']['factory'] = {
    'handlers': ['null'],
    'propagate': False,
    'level': 'ERROR',
}
LOGGING['loggers']['boto3'] = {
    'handlers': ['console'],
    'propagate': False,
    'level': 'ERROR',
}
LOGGING['loggers']['botocore'] = {
    'handlers': ['console'],
    'propagate': False,
    'level': 'ERROR',
}
