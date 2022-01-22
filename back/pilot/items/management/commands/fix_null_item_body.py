import logging
import sys
import itertools

from django.core.management.base import BaseCommand
from django.db import models, transaction

from pilot.utils.prosemirror.prosemirror import EMPTY_PROSEMIRROR_DOC
from pilot.items.models import Item, EditSession


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fix incorrect null body in item contents'

    requires_system_checks = False

    def handle(self, *fixture_labels, **options):
        logger.info(f"[Command Start] {' '.join(sys.argv[1:])}")

        i = 0
        with transaction.atomic():
            for model in (Item, EditSession):
                for instance in itertools.chain(
                    model.objects.exclude(json_content__has_key='body'),
                    model.objects.filter(json_content__contains={'body': None}),
                ):
                    instance.json_content['body'] = EMPTY_PROSEMIRROR_DOC
                    # Don't use directly item_content.save, this would create edit session
                    # And erase updated_at
                    models.Model.save(instance)

                    i += 1
                    if (i % 10) == 0:
                        print("done {}".format(i))


        logger.info(f"[Command End] {' '.join(sys.argv[1:])}")

