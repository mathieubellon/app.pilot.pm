import logging
import sys

from django.core.management.base import BaseCommand

from pilot.utils.search import run_search_vector_update

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Update the search vector for instances that has been previously saved
    """

    help = "Update the search vector for instances that has been previously saved"

    def handle(self, *args, **options):
        logger.info(f"[Cron Command Start] {' '.join(sys.argv[1:])}")

        run_search_vector_update()

        logger.info(f"[Cron Command End] {' '.join(sys.argv[1:])}")
