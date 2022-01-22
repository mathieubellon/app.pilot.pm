import logging
import sys
import arrow
from django.core.exceptions import ObjectDoesNotExist

from django.core.management.base import BaseCommand
from django.db import transaction

from pilot.desks.models import Desk
from pilot.organizations.models import Organization
from pilot.pilot_users.models import PilotUser, UserInOrganization
from pilot.utils.s3 import delete_s3_file, delete_s3_folder

logger = logging.getLogger(__name__)



class Command(BaseCommand):
    help = 'Totally delete a desk and its orphan users'

    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('-d', '--desk', required=True,
            help='Desk id to delete')

    def handle(self, *fixture_labels, **options):
        logger.info(f"[Command Start] {' '.join(sys.argv[1:])}")

        print("Gathering data...")

        desk_id = options['desk']
        try:
            desk = Desk.objects.get(pk=desk_id)
        except ObjectDoesNotExist:
            exit(f"No desk found with id {desk_id}")

        try:
            latest_activity = arrow.get(desk.activity_stream.latest('created_at').created_at).format('DD/MM/YYYY HH:MM')
        except ObjectDoesNotExist:
            latest_activity = "NEVER"

        assets_count = desk.assets.count()

        print(
            f"This command will PERMANENTLY delete the desk \"{desk.name}\" ( id={desk.id} ) and ALL ASSOCIATED DATA.\n"
            f"{desk.projects.count()} Projects\n"
            f"{desk.items.count()} Items\n"
            f"{assets_count} Assets\n"
            f"{desk.users.count()} Users\n"
            f"Last activity : {latest_activity}\n"
        )

        desk_name = None
        while desk_name != desk.name:
            print("!! WARNING !! No turning back after the confirmation. Please think twice !")
            print("Confirm the TOTAL DESTRUCTION by typing the desk name ( or CTRL+C to exit ) :")
            desk_name = input()

        users = list(desk.users.all())
        organization = desk.organization

        with transaction.atomic():
            print("Deleting s3 files (this may takes a while)")
            delete_s3_folder(f'assets/{desk.id}/')
            delete_s3_folder(f'export/{desk.id}/')
            delete_s3_file(str(desk.logo))

            print("Deleting pilot db data")
            # Will delete in cascade all other related objects, directly in the db.
            desk.delete()

            if organization.desks.count() == 0:
                organization.delete()

            print("Deleting orphan users and their avatar")
            for user in users:
                if user.desks.count() == 0:
                    delete_s3_file(str(user.avatar))
                    user.delete()

        print(F"Done. The desk {desk_name} has been destroyed. RIP !")
        logger.info(f"[Command End] {' '.join(sys.argv[1:])}")




