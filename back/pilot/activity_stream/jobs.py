import logging

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from pilot.activity_stream.models import Activity
from pilot.pilot_users.models import PilotUser

logger = logging.getLogger(__name__)


def create_activity(actor, desk, verb, target=None, target_str='',
                    action_object=None, action_object_str='',
                    diff=None):
    """
    Create an Activity instance, synchronously or inside a Job in the Queue.

    28/01/19 : Activity creation is now always synchroneous until we can fix issues with lost jobs
    """
    try:
        activity = Activity(
            desk=desk,
            verb=verb,
            target=target,
            target_str=target_str,
            action_object=action_object,
            action_object_str=action_object_str,
            diff=diff
        )

        if isinstance(actor, PilotUser):
            activity.actor = actor
        elif actor in Activity.NON_DB_USERS:
            activity.actor_identifier = actor
        else:
            try:
                validate_email(actor)
                activity.actor_email = actor
            except ValidationError:
                raise ValueError("Actor must be a PilotUser instance or a NON_DB_USERS or an email.")

        activity.save()

        # De-activated for now
        # from pilot.notifications.feed import notify_activity_feeds
        # notify_activity_feeds(activity)

        return activity

    except Exception as e:
        logger.error('Error while trying to create an Activity', exc_info=True)
