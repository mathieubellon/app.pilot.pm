import logging
import sys

import itertools
import json

from django.core.management.base import BaseCommand
from django.db import models, transaction

from pilot.items.models import ItemType, Item, EditSession

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix incorrect data for multi_checkboxes in item contents'

    requires_system_checks = False

    def handle(self, *fixture_labels, **options):
        logger.info(f"[Command Start] {' '.join(sys.argv[1:])}")

        with transaction.atomic():
            for custom_type in ItemType.objects.all():
                checkbox_fields = []

                for field_schema in custom_type.schema:
                    if field_schema['type'] == 'multi_checkboxes':
                        checkbox_fields.append(field_schema['name'])

                if checkbox_fields:
                    print("Starting Item type {} on fields {}".format(custom_type, checkbox_fields))
                    for i, item_content in enumerate(itertools.chain(
                        Item.all_the_objects.filter(item_custom_type=custom_type).iterator(),
                        EditSession.objects.filter(item_custom_type=custom_type).iterator()
                    )):
                        for checkbox_field in checkbox_fields:
                            # Old item content where the schema did not had this key
                            if checkbox_field not in item_content.json_content:
                                continue

                            value = item_content.json_content[checkbox_field]

                            # No corruption here
                            if isinstance(value, list):
                                continue

                            if value is None or value == "":
                                new_value = []

                            elif isinstance(value, str):
                                try:
                                    new_value = json.loads(value)
                                except:
                                    raise Exception("json decode error\n{} id {}\nfield {}\nvalue {}".format(
                                        item_content.__class__.__name__,
                                        item_content.id,
                                        checkbox_field,
                                        value
                                    ))

                            else:
                                raise Exception("Unknown value : {}".format(value))

                            item_content.json_content[checkbox_field] = new_value

                        # Don't use directly item_content.save, this would create item sessions
                        # And erase updated_at
                        models.Model.save(item_content)

                        if (i % 50) == 0:
                            print("done {}".format(i))

        logger.info(f"[Command End] {' '.join(sys.argv[1:])}")
