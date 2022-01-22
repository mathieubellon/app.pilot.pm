import logging
import sys

import arrow
from django.core.management.base import BaseCommand

from pilot.queue.models import JobTracker


logger = logging.getLogger(__name__)


UNFINISHED_STATE = [
    JobTracker.STATE_QUEUED,
    JobTracker.STATE_STARTED,
]


class Command(BaseCommand):
    """
    Monitor zombie jobs, and re-launch them as needed
    """

    help = "Monitor zombie jobs, and re-launch them as needed"

    def handle(self, *args, **options):
        """
        Zombie jobs are :
         - running for more than one hour
         - failed jobs
        """
        logger.info(f"[Cron Command Start] {' '.join(sys.argv[1:])}")

        zombification_date = arrow.now().shift(hours=-2)

        # Any job which is not finished 2 hours after its creation is considered a zombie
        for job_tracker in JobTracker.objects.filter(
            state__in=UNFINISHED_STATE,
            created_at__lte=zombification_date.datetime
        ):
            job_tracker.state = JobTracker.STATE_ZOMBIE

            # We try 3 times before definitely considering this job a zombie
            if job_tracker.try_count < 3:
                job_tracker.try_count += 1
                job_tracker.requeue()
            # Already 3 retries, it's now officially a zombie
            else:
                job_tracker.save()
                logger.error("A zombie job has been detected : {}".format(job_tracker))

        logger.info(f"[Cron Command End] {' '.join(sys.argv[1:])}")
