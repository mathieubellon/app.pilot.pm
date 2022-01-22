import logging
import sys

from django.core.management.base import BaseCommand
from django.db import transaction

from pilot.desks.models import Desk
from pilot.organizations.models import Organization
from pilot.pilot_users.models import PilotUser, UserInOrganization

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Change the organization of a desk and its users'

    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('-d', '--desk', required=True,
            help='Desk id to reassign')
        parser.add_argument('-o', '--organization', required=True,
            help='Destination organization id')

    def handle(self, *fixture_labels, **options):
        logger.info(f"[Command Start] {' '.join(sys.argv[1:])}")

        desk_id = options['desk']
        organization_id = options['organization']

        # Ensure the destination user exists
        desk = Desk.objects.get(pk=desk_id)
        organization = Organization.objects.get(pk=organization_id)

        print("Reassigning desk {} onto organization {}".format(
            desk,
            organization
        ))

        with transaction.atomic():
            desk.organization = organization
            desk.save()

            UserInOrganization.objects.filter(
                user__in=desk.users.all()
            ).update(organization=organization)

        logger.info(f"[Command End] {' '.join(sys.argv[1:])}")




