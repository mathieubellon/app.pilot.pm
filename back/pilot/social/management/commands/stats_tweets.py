from optparse import make_option
import pprint

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from pilot.desks.models import Desk
from pilot.social.models import TweetLog
# from pilot.utils.custom_tweepy import CustomAPI

BLOCK_SIZE = 100  # Number of tweet ids allowed by `status/lookup` method

MAX_REQUESTS_PER_QUARTER = 180  #

DELAY = 15 * 60  # Seconds


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
                            help='display only, no publishing')

    def _make_log_dict(self, tweet):
        log_dict = {
            'text': tweet.text,
            'id': tweet.id,
            'retweeted': tweet.retweeted,
            'retweet_count': tweet.retweet_count,
            'favorite_count': tweet.favorite_count,
            'favorited': tweet.favorited,
            'geo': tweet.geo,
            'place': tweet.place,
        }

        return log_dict

    def _gather_stats(self, lookup):
        """

        """
        for index, tweet in enumerate(lookup):

            log_dict = self._make_log_dict(tweet)

            if self.verbosity == 1:
                self.stdout.write("{0} Tweet data for {1}".format(index, tweet.id))
            if self.verbosity > 1:
                self.stdout.write("Tweet data")
                ppr = pprint.PrettyPrinter(indent=4)
                ppr.pprint(log_dict)
            tlog = TweetLog.objects.get(tweet_id=tweet.id)
            tlog.info = log_dict
            tlog.last_checked = timezone.now()
            tlog.save()
            self.tweets_processed += 1

    def _get_queryset(self, desk, channel):
        """
        Gets the logs for published tweets, at first those whithout stats and those which were checked in the past
        """
        tweetlogs = TweetLog.objects.filter(
            item__desk=desk,
            item__channel=channel,
            status=TweetLog.PUBLISHED_STATUS
        ).extra(
            select={'has_last_checked': "CASE WHEN last_checked IS NULL THEN 1 ELSE 0 END"}
        ).order_by(
            '-has_last_checked',
            'last_checked'
        )
        return tweetlogs

    def _get_stats_for_desk(self, desk, desks_count, **options):
        self.stdout.write(u"Get twitter stats for desk: {0}".format(desk))

        credentials_list = TwitterCredential.valid.for_desk(desk)

        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)

        for credentials in credentials_list:
            self.stdout.write(u"Get twitter stats for channel : {0}".format(credentials.channel))

            auth.set_access_token(credentials.access_token_key, credentials.access_token_secret)

            api = CustomAPI(auth)
            api_is_valid = False

            try:
                api_is_valid = api.verify_credentials()
            except Exception as error:
                self.stdout.write(u"Credentials error : {0} - {1}".format(credentials, error))
            if not api_is_valid:
                self.stdout.write(u"Credentials : {0} is invalid".format(credentials))
                continue

            tweet_queryset = self._get_queryset(desk, credentials.channel)

            for t in tweet_queryset:
                self.stdout.write("Id: {0} Last checked {1}".format(t, t.last_checked))
            self.stdout.write("{0} logs to process ".format(len(tweet_queryset)))

            requests_per_desk_and_quarter = int(MAX_REQUESTS_PER_QUARTER / desks_count)
            queryset_limit = BLOCK_SIZE * requests_per_desk_and_quarter
            tweet_objects = get_chunks(tweet_queryset[:queryset_limit], BLOCK_SIZE)
            for tweet_chunks in tweet_objects:
                tweet_list = [t.tweet_id for t in tweet_chunks]

                if self.verbosity > 1:
                    self.stdout.write("Tweet list : {0}".format(tweet_list))
                tweet_list_string = ','.join([str(int(tweet)) for tweet in tweet_list])

                # We use the POST statuses/lookup  https://dev.twitter.com/docs/api/1.1/get/statuses/lookup
                # This method is especially useful to get the details (hydrate) a collection of Tweet IDs.
                if not options['dry_run']:
                    lookup = api.status_lookup(tweet_list_string)
                    self.queries += 1
                    self._gather_stats(lookup)

    def handle(self, *args, **options):
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
        for desk_id in desk_list:
            self._get_stats_for_desk(desk_id, desks_count, **options)

        self.stdout.write("Requests on twitter api {0}".format(self.queries))
        self.stdout.write("Tweets processed {0}".format(self.tweets_processed))
