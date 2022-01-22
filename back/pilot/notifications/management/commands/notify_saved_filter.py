import logging
import sys

from django.core.management.base import BaseCommand

from pilot.notifications.jobs import run_notify_saved_filter

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Notify users when items are impacted in a saved filter
    """

    help = "Notify users when items are impacted in a saved filter"

    def handle(self, *args, **options):
        logger.info(f"[Cron Command Start] {' '.join(sys.argv[1:])}")

        run_notify_saved_filter()

        logger.info(f"[Cron Command End] {' '.join(sys.argv[1:])}")
