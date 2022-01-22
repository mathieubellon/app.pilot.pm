from PIL import Image

from django.db import transaction

from pilot.pilot_users.models import PilotUser
from settings.base import backend_path

PILOT_BOT_EMAIL = "pilotbot@pilot.pm"
PILOT_BOT_USERNAME = "pilotbot"
PILOT_BOT_AVATAR = backend_path('pilot', 'notifications', 'pilot_bot.png')
# Once created or retrieved, the pilot bot user will never change,
# Just cache it in memory
cached_pilot_bot = None


def get_pilot_bot_user():
    global cached_pilot_bot

    # First call, get or create the pilot bot user, then cache it in memory
    if not cached_pilot_bot:
        try:
            cached_pilot_bot = PilotUser.objects.get(email=PILOT_BOT_EMAIL)
        except PilotUser.DoesNotExist:
            with transaction.atomic():
                # Create an id upfront for the avatar file naming
                cached_pilot_bot = PilotUser.objects.create(
                    email=PILOT_BOT_EMAIL,
                    username=PILOT_BOT_USERNAME
                )

                # Now that we have an id, we can save the avatar
                img = Image.open(PILOT_BOT_AVATAR)
                img.thumbnail(PilotUser.AVATAR_SIZE, Image.ANTIALIAS)
                cached_pilot_bot._update_avatar(img)
                cached_pilot_bot.save()

    if not cached_pilot_bot.pk:
        cached_pilot_bot = None
        raise Exception("Pilot Bot user has not been created properly")

    return cached_pilot_bot
