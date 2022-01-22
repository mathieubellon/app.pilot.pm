import logging
import sys

import arrow
from django.core.management.base import BaseCommand

from pilot.notifications.models import Reminder
from pilot.notifications.notify import notify_ripe_reminder


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check for reminders that are ripe for notification (the notification time is reached)'

    requires_system_checks = False

    def handle(self, *fixture_labels, **options):
        logger.info(f"[Cron Command Start] {' '.join(sys.argv[1:])}")

        now = arrow.utcnow()

        ripe_reminders = (
            Reminder.objects
            .filter(notification=None)  # No notification sent yet
            .filter(cancelled=False)  # The reminder has not been cancelled
            .filter(ripe_date_time__lte=now.datetime)  # The notification time has been reached
        )

        for reminder in ripe_reminders:
            notifications_sent = notify_ripe_reminder(reminder)
            reminder.is_notification_sent = True
            if len(notifications_sent) > 0:
                reminder.notification = notifications_sent[0]
            reminder.save()

        logger.info(f"[Cron Command End] {' '.join(sys.argv[1:])}")
