import logging
import sys

from django.core.management.base import BaseCommand, CommandError
from django.contrib.sessions.models import Session

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = '<session_key>'
    help = ("Delete user session")

    def handle(self, *args, **options):
        logger.info(f"[Command Start] {' '.join(sys.argv[1:])}")

        for session_key in args:
            try:
                session = Session.objects.get(session_key=session_key)
            except Session.DoesNotExist:
                raise CommandError('Session "%s" does not exist' % session_key)

            session.delete()

            self.stdout.write('Successfully deleted session "%s"' % session_key)

        logger.info(f"[Command End] {' '.join(sys.argv[1:])}")
