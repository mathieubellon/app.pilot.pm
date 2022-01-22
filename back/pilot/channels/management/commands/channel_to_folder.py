import logging
import sys

from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.core.management.base import BaseCommand
from django.db import transaction

from pilot.channels.models import Channel
from pilot.utils.projel.hierarchy import ensure_consistent_hierarchy, sort_hierarchy

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('-s', '--source', required=True,
            help='Source channel id')
        parser.add_argument('-d', '--destination', required=True,
            help='Destination channel id')


    def handle(self, *args, **options):
        logger.info(f"[Command Start] {' '.join(sys.argv[1:])}")

        source_channnel_id = options['source']
        destination_channnel_id = options['destination']

        source_channnel = Channel.objects.get(id=source_channnel_id)
        destination_channnel = Channel.objects.get(id=destination_channnel_id)

        with transaction.atomic():

            item_ids = []
            for item in source_channnel.items.all():
                if destination_channnel not in item.channels.all():
                    item.channels.add(destination_channnel)
                    item_ids.append(item.id)

            destination_channnel.hierarchy.append(
                {
                    'type': 'folder',
                    'name': source_channnel.name,
                    'nodes': [
                        {
                            'type': 'item',
                            'id': item_id
                        }
                        for item_id in item_ids
                    ]
                }
            )
            destination_channnel.save()
            ensure_consistent_hierarchy(destination_channnel)

        logger.info(f"[Command End] {' '.join(sys.argv[1:])}")


