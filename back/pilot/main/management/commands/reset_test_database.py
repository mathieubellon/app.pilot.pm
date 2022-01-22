import os
import glob
import imp

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from django.utils.functional import cached_property

from django.contrib.sites.models import Site

from pilot.desks.tests import factories as desks_factories

def noop(*args, **kwargs): pass

class Command(BaseCommand):
    help = 'Reset the test database between each nightwatch test'

    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('args', metavar='fixture', nargs='*',
            help='Path(s) to fixtures to load before running the server.')

    def handle(self, *fixture_labels, **options):
        verbosity = options.get('verbosity')

        test_database_name = connection.creation._get_test_db_name()
        settings.DATABASES[connection.alias]["NAME"] = test_database_name
        connection.settings_dict["NAME"] = test_database_name

        # Fix a weird bug where content_type is incorrect after the flush,
        # And the post_migrate signal try to recreate some already existing ContentTypes
        ContentType.objects.all().delete()

        # Wipe clean the whole database
        call_command('flush', interactive=False)

        # Init the base test data
        desks_factories.DeskFactory.create()

        # Load the fixture data into the test database, if any
        if fixture_labels:
            self.load_fixtures(fixture_labels)

    def load_fixtures(self, fixture_labels):
        for fixture_label in fixture_labels:
            loader_name, fixture_name = fixture_label.split('.')
            fixture_loader = self.fixtures_loaders.get(loader_name)
            if not fixture_loader:
                continue
            getattr(fixture_loader, fixture_name, noop)()

    @cached_property
    def fixtures_loaders(self):
        loaders = {}

        for app_config in apps.get_app_configs():
            app_dir = os.path.join(app_config.path, 'tests', 'nightwatch_fixtures')

            if not os.path.isdir(app_dir):
                continue

            modules = glob.glob(app_dir + "/*.py")
            for module_path in modules:
                module_name = os.path.basename(module_path)
                if module_name[-3:] != '.py':
                    continue
                module_name = module_name[:-3]
                loaders[module_name] = imp.load_source('nightwatch_fixtures.' + module_name, module_path)

        return loaders


