import logging
import sys

from django.core.management.base import BaseCommand

from pilot.demo.deserializer import load_demo_desk


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Load an entire desk from json files for the demo site
    """

    help = "Load an entire desk from json files for the demo site"

    def handle(self, *args, **options):
        logger.info(f"[Cron Command Start] {' '.join(sys.argv[1:])}")

        load_demo_desk()

        logger.info(f"[Cron Command End] {' '.join(sys.argv[1:])}")
