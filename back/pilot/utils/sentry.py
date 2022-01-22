import os
import subprocess

SENTRY_RELEASE = None

try:
    # On Heroku
    SENTRY_RELEASE = os.environ.get('HEROKU_SLUG_COMMIT', None)

    # On other env with git
    if SENTRY_RELEASE is None:
        SENTRY_RELEASE = subprocess.check_output(['git', 'rev-parse', '--short=10', 'HEAD']).decode().strip()

    if SENTRY_RELEASE:
        SENTRY_RELEASE = SENTRY_RELEASE[0:10]
except:
    SENTRY_RELEASE = None
