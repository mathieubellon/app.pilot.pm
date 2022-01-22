import logging
import sys

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import models, transaction

from pilot.pilot_users.models import PilotUser

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Merge multiple users into one'

    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('-d', '--destination', required=True,
            help='Destination user id')
        parser.add_argument('-s', '--source', required=True,
            help='Source user ids, as a comma-separated list of ids')

    def handle(self, *fixture_labels, **options):
        logger.info(f"[Command Start] {' '.join(sys.argv[1:])}")

        destination_user_id = options['destination']
        source_users_ids = options['source'].split(',')

        # Ensure the destination user exists
        destination_user = PilotUser.objects.get(pk=destination_user_id)
        source_users = PilotUser.objects.filter(pk__in=source_users_ids)

        print("Redirecting users {} onto user {}".format(
            ', '.join([str(u) for u in source_users]),
            destination_user
        ))

        with transaction.atomic():
            all_models = apps.get_models(include_auto_created=True)

            for model in all_models:
                for field in model._meta.get_fields():
                    if isinstance(field, models.ForeignKey) and field.related_model == PilotUser:
                        print("Reassigning field {} on model {}...".format(field.name, model._meta.object_name), end='')

                        affected_rows = model.objects.filter(**{
                            field.name + '__in': source_users_ids
                        }).update(**{
                            field.name: destination_user_id
                        })

                        print(" Done on {} rows".format(affected_rows))

        logger.info(f"[Command End] {' '.join(sys.argv[1:])}")
