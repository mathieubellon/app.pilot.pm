import logging
import sys

from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session

from pilot.pilot_users.models import PilotUser

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = ("List all sessions->users map.")

    def handle(self, verbosity=0, **kwargs):
        logger.info(f"[Command Start] {' '.join(sys.argv[1:])}")

        sessions = Session.objects.all()

        for session in sessions:
            session = Session.objects.get(session_key=session.pk)
            uid = session.get_decoded().get('_auth_user_id')

            if uid is not None:
                user = PilotUser.objects.get(pk=uid)
                print('{0} -> {1}'.format(session.session_key, user.email))
            else:
                pass

        logger.info(f"[Command End] {' '.join(sys.argv[1:])}")
