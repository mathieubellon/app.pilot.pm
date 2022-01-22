import logging
import sys

from django.core.management.base import BaseCommand
from django.db import connection

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Help reduce the size of the DB by running a VACUUM and (optionally) REINDEX on all tables'

    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('--full',
            action='store_true', dest='full', default=False,
            help='Use VACUUM with the FULL options, which is a more significant cleaning, '
                 'but which will incur an EXCLUSIVE LOCK on each table')

        parser.add_argument('--reindex',
            action='store_true', dest='reindex', default=False,
            help='Launch a full REINDEX on the database (on all the tables). '
                 'This incur a write-lock on the tables during the reindexation.')

    def handle(self, *fixture_labels, **options):
        logger.info(f"[Cron Command Start] {' '.join(sys.argv[1:])}")

        with connection.cursor() as cursor:
            if options.get('full'):
                cursor.execute("VACUUM FULL")
            else:
                cursor.execute("VACUUM")

            if options.get('reindex'):
                cursor.execute("REINDEX DATABASE {}".format(connection.settings_dict['NAME']))

        logger.info(f"[Cron Command End] {' '.join(sys.argv[1:])}")

