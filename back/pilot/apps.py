from django.apps import AppConfig

# We import this here to ensure the reactor is installed very early on
# in case other packages accidentally import twisted.internet.reactor
# (e.g. raven does this).
import daphne.server

assert daphne.server  # pyflakes doesn't support ignores


class DjangoChannelsConfig(AppConfig):

    name = "channels"
    verbose_name = "Channels"
    label = 'django_channels'

    def ready(self):
        # Do django monkeypatches
        from channels.hacks import monkeypatch_django

        monkeypatch_django()
