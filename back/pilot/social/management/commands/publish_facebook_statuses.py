import warnings

# import facebook

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from pilot.activity_stream.models import Activity

from pilot.social.models import FacebookLog

THROTTLE = getattr(settings, "FACEBOOK_THROTTLE", 3)

warnings.filterwarnings(
    'error', r"DateTimeField .* received a naive datetime",
    RuntimeWarning, r'django\.db\.models\.fields')


class Command(BaseCommand):
    help = "Publish items associated to a facebook channel."

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('--dry-run',
                            action='store_true',
                            dest='dry_run',
                            default=False,
                            help='display only, no publishing')

    def handle(self, *args, **options):

        credentials_list = FacebookCredential.valid.all()

        for credentials in credentials_list:

            api = facebook.GraphAPI(credentials.get_relevant_token())

            api_is_valid = False
            statuses_to_publish = []

            try:
                api_is_valid = api.get_object('me')
            except facebook.GraphAPIError as e:
                self.stdout.write(u"Credentials error : {0} - {1}".format(credentials, e))

            if api_is_valid:
                statuses_to_publish = item_models.Item.publishable_facebook_statuses.for_channel(
                    credentials.channel)[:THROTTLE]
                statuses_string = ",".join([u"{0}".format(t) for t in statuses_to_publish])
                self.stdout.write(
                    u"Facebook account '{0}', statuses_to_publish {1}\n".format(
                        credentials.get_relevant_name(),
                        statuses_string),
                )

            for fb_status in statuses_to_publish:
                self.stdout.write(u"Facebook status: {0}\n".format(fb_status))
                message = fb_status.body.encode()
                status = False

                if options['dry_run']:
                    break
                try:
                    status = api.put_object(credentials.get_relevant_id(), 'feed', message=message)
                except Exception as error:
                    fb_status_id = 'none'
                    text = error
                    log_status = FacebookLog.ERROR_STATUS
                    fb_status.external_publication_error = '[{"message" : "%s"}]' % format(error)
                    fb_status.save()
                if status:
                    fb_status.publish(non_db_user=Activity.SYSTEM_USER)
                    # We log the transition with a string instead of a db user
                    fb_status.publication_dt = timezone.now()
                    fb_status.external_publication_error = None
                    fb_status.save()

                    fb_status_id = status['id']
                    text = fb_status.body
                    log_status = FacebookLog.PUBLISHED_STATUS
                    self.stdout.write(u"facebook_status {0} published\n".format(text))

                FacebookLog.objects.create(item=fb_status, status_id=fb_status_id, text=text, status=log_status)
