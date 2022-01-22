import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from pilot.desks.models import Desk


class Command(BaseCommand):
    args = '[desk_id desk_id ...]>'
    help = "Get rate limit for twitter api. "

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('--verbosity',
                            action='store',
                            dest='verbosity',
                            default=0,
                            type='choice',
                            choices=['0', '1'],
                            help='Verbosity level; 0=minimal output, 1=normal output')

    def get_rate_for_desk(self, desk):
        credentials_list = TwitterCredential.valid.for_desk(desk)

        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)

        for credentials in credentials_list:
            auth.set_access_token(credentials.access_token_key, credentials.access_token_secret)

            api = tweepy.API(auth)
            api_is_valid = False

            try:
                api_is_valid = api.verify_credentials()
            except Exception as error:
                self.stdout.write("Credentials error : {0} - {1}".format(credentials, error))
            if not api_is_valid:
                self.stdout.write("Credentials : {0} is invalid".format(credentials))
                continue

            response = api.rate_limit_status()
            status = response['resources']['statuses']['/statuses/lookup']
            self.stdout.write("Rate limit for lookup (channel {0}) : {1}".format(credentials.channel, status))
            reset_dt = datetime.datetime.fromtimestamp(status["reset"]).strftime('%Y-%m-%d %H:%M:%S')
            self.stdout.write("Reset at {0}".format(reset_dt))

    def handle(self, *args, **options):
        if not args:
            desk_list = Desk.objects.all()
            for desk_id in desk_list:
                self.get_rate_for_desk(desk_id)
            exit(1)

        for desk_id in args:
            try:
                desk = Desk.objects.get(id=desk_id)
            except Desk.DoesNotExist:
                self.stdout.write("Desk {0} does not exist".format(desk_id))
                continue
            self.get_rate_for_desk(desk)
