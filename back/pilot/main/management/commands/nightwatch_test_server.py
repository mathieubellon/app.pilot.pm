from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings

from settings.base import frontend_path


class Command(BaseCommand):
    help = 'Runs a development server for nightwatch.js functional test suite'

    requires_system_checks = False

    def add_arguments(self, parser):
        parser.add_argument('--noinput', '--no-input',
            action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.')
        parser.add_argument('--addrport', default='',
            help='Port number or ipaddr:port to run the server on.')
        parser.add_argument('--ipv6', '-6', action='store_true', dest='use_ipv6', default=False,
            help='Tells Django to use an IPv6 address.')
        parser.add_argument('-k', '--keepdb', action='store_true', dest='keepdb',default=False,
            help='Preserves the test DB between runs.')
        parser.add_argument('--use_webpack_server', action='store_true', dest='use_webpack_server',default=False,
            help='Instead of the compiled static bundle, use to the webpack dev server')

    def handle(self, *fixture_labels, **options):
        verbosity = options.get('verbosity')
        interactive = options.get('interactive')
        use_webpack_server = options.get('use_webpack_server')

        if use_webpack_server:
            settings.WEBPACK_LOADER['DEFAULT']['STATS_FILE'] = frontend_path('webpack-stats-dev.json')

        # Create a test database.
        db_name = connection.creation.create_test_db(
            verbosity=verbosity,
            autoclobber=not interactive,
            serialize=False,
            keepdb=options['keepdb']
        )

        # Run the development server. Turn off auto-reloading because it causes
        # a strange error -- it causes this handle() method to be called
        # multiple times.
        shutdown_message = (
            '\nServer stopped.\nNote that the test database, %r, has not been '
            'deleted. You can explore it on your own.' % db_name
        )
        use_threading = connection.features.test_db_allows_multiple_connections
        call_command(
            'runserver',
            addrport=options['addrport'],
            shutdown_message=shutdown_message,
            use_reloader=False,
            use_ipv6=options['use_ipv6'],
            #use_threading=use_threading
            use_threading=False,
            insecure_serving=True
        )
