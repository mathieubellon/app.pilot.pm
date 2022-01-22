import logging
from optparse import make_option
import pprint
import time

from django.core.management.base import BaseCommand
from django.utils import timezone

# import facebook

from pilot.desks.models import Desk
from pilot.social.models import FacebookLog

MAX_REQUESTS_PER_BATCH = 200


def get_chunks(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


class Command(BaseCommand):
    args = '[desk_id desk_id ...]>'
    help = "Get statistics for tweets.\n" \
           "At first this script checks tweets which don't have any stats then the older ones\n\n" \
           "Pass --dry-run argument to get information about tweet to check "

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('--dry-run',
                            action='store_true',
                            dest='dry_run',
                            default=False,
                            help='Delete poll instead of closing it')

    def _gather_stats(self, response, status):
        if self.verbosity == 1:
            self.stdout.write("Facebook data for {0}".format(status.status_id))
        if self.verbosity > 1:
            self.stdout.write("Facebook data")
            ppr = pprint.PrettyPrinter(indent=4)
            ppr.pprint(response)

        status.info = response
        status.last_checked = timezone.now()
        status.save()
        self.tweets_processed += 1

    def _get_queryset(self, desk, channel):
        """
        Gets the logs for published tweets, at first those whithout stats and those which were checked in the past
        """
        facebooklogs = FacebookLog.objects.filter(
            item__desk=desk,
            item__channel=channel,
            status=FacebookLog.PUBLISHED_STATUS
        ).extra(
            select={'has_last_checked': "CASE WHEN last_checked IS NULL THEN 1 ELSE 0 END"}
        ).order_by(
            '-has_last_checked',
            'last_checked'
        )
        return facebooklogs

    def _get_stats_for_desk(self, desk, desks_count, **options):
        self.stdout.write(u"Get facebook stats for desk: {0}".format(desk))

        credentials_list = FacebookCredential.valid.for_desk(desk)

        api_is_valid = False

        for credentials in credentials_list:
            api = facebook.GraphAPI(credentials.get_relevant_token())

            self.stdout.write(u"Get facebook stats for channel : {0}".format(credentials.channel))

            try:
                api_is_valid = api.get_object('me')
            except facebook.GraphAPIError as e:
                self.logger.error(u"Credentials error : {0} - {1}".format(credentials, e))

            if not api_is_valid:
                self.stdout.write(u"Credentials : {0} is invalid".format(credentials))
                continue

            facebook_queryset = self._get_queryset(desk, credentials.channel)

            for t in facebook_queryset:
                last_checked = t.last_checked.strftime("%d-%m-%Y %H:%M:%S") if t.last_checked else u"Never"
                self.stdout.write("Id: {0} Last checked {1}".format(t, last_checked))
            self.stdout.write("{0} logs to process ".format(len(facebook_queryset)))

            queryset_limit = int(MAX_REQUESTS_PER_BATCH / desks_count)
            facebook_objects = facebook_queryset[:queryset_limit]
            for status in facebook_objects:
                if not options['dry_run']:
                    try:
                        response = api.get_object(status.status_id, fields='likes.summary(true),shares')
                        self._gather_stats(response, status)
                    except facebook.GraphAPIError as e:
                        self.logger.error(u"Graph api error: {0}".format(e))

                    time.sleep(1)  # No official clue about rate limit - SO answer indicates 1 request/second to be safe
                    self.queries += 1

    def handle(self, *args, **options):
        self.logger = logging.getLogger(__name__)
        self.verbosity = int(options.get('verbosity', 0))
        self.queries = 0
        self.tweets_processed = 0

        if not args:
            desk_list = Desk.objects.all()

        for desk_id in args:
            desk_list = []
            try:
                desk = Desk.objects.get(id=desk_id)
                desk_list.append(desk)
            except Desk.DoesNotExist:
                self.stdout.write("Desk {0} does not exist".format(desk_id))

        desks_count = len(desk_list)
        self.logger.info("Beginning facebook stats gathering")
        for desk_id in desk_list:
            self._get_stats_for_desk(desk_id, desks_count, **options)

        self.stdout.write("Requests on facebook api {0}".format(self.queries))
        self.stdout.write("Statuses processed {0}".format(self.tweets_processed))
        self.logger.info("End of facebook stats gathering")
