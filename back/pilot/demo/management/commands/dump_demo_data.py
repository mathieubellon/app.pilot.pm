import logging
import sys

from django.core.management.base import BaseCommand

from pilot.desks.models import Desk
from pilot.demo.serializer import dump_demo_desk


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Dump an entire desk into json files for the demo site
    """

    help = "Dump an entire desk into json files for the demo site"

    def add_arguments(self, parser):
        parser.add_argument('-d', '--desk', required=True, help='Desk id to dump')

    def handle(self, *args, **options):
        logger.info(f"[Command Start] {' '.join(sys.argv[1:])}")

        desk_id = options['desk']
        desk = Desk.objects.get(pk=desk_id)
        dump_demo_desk(desk)

        logger.info(f"[Command End] {' '.join(sys.argv[1:])}")
