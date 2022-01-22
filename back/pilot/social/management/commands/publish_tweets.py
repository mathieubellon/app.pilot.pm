import ast
import json
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from pilot.activity_stream.models import Activity

from pilot.social.models import TweetLog

THROTTLE = getattr(settings, "TWITTER_THROTTLE", 3)


class Command(BaseCommand):
    help = "Publish items associated to a twitter channel.\n\n" \
           "Do not exceed 2400 tweets a day and 100 tweets an hour"

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('--dry-run',
                            action='store_true',
                            dest='dry_run',
                            default=False,
                            help='display only, no publishing')

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)

        credentials_list = TwitterCredential.valid.all()

        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)

        for credentials in credentials_list:
            auth.set_access_token(credentials.access_token_key, credentials.access_token_secret)

            api = tweepy.API(auth)
            api_is_valid = False
            tweets_to_publish = []

            try:
                api_is_valid = api.verify_credentials()
            except Exception as error:
                self.stdout.write(u"Credentials error : {0} - {1}".format(credentials, error))

            if api_is_valid:
                tweets_to_publish = item_models.Item.publishable_tweets.for_channel(credentials.channel)[:THROTTLE]
                tweets_string = ",".join([u"{0}".format(t) for t in tweets_to_publish])
                self.stdout.write(u"Twitter account '{0}', tweets_to_publish {1}\n".format(credentials, tweets_string))

            for tw in tweets_to_publish:
                self.stdout.write(u"Twitter channel '{0}', twitt \n".format(tw.channel))

                status = False
                if not options['dry_run']:
                    try:
                        status = api.update_status(tw.body)
                    except tweepy.TweepError as error:
                        tweet_id = 'none'
                        text = error
                        log_status = TweetLog.ERROR_STATUS
                        error = error.reason

                        # The Tweepy api  returns single quoted chars so we need a trick
                        # we use python ast module to evaluate the string as a data structure before dumping
                        # it with json module. The ast.literal_eval() method is said to be safe and does not evaluate
                        # malicious code but data structures
                        try:
                            error_list = ast.literal_eval(error.strip())
                        except Exception as e:
                            logger.error(e)
                        tw.external_publication_error = json.dumps(error_list)
                        tw.save()
                    if status:
                        tw.publish(non_db_user=Activity.SYSTEM_USER)
                        # We log the transition with a string instead of a db user
                        tw.publication_dt = timezone.now()
                        tw.save()

                        tweet_id = status.id
                        text = status.text
                        log_status = TweetLog.PUBLISHED_STATUS
                        self.stdout.write(u"tweets_to_publish {0} published\n".format(text))
                    tw.tweetlog_set.all().delete()
                    TweetLog.objects.create(item=tw, tweet_id=tweet_id, text=text, status=log_status)
