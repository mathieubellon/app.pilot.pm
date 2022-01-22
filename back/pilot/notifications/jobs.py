import logging

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from pilot.utils.redis import redis_client

from pilot.queue import jobs_registar
from pilot.queue.jobs import Job
from pilot.queue.rq_setup import high_priority_queue

logger = logging.getLogger(__name__)


NOTIFY_SAVED_FILTER_REDIS_KEY = 'pilot:notify_saved_filter'


class NotifyJob(Job):
    job_type = jobs_registar.JOB_TYPE_NOTIFY
    queue = high_priority_queue
    delete_tracker_on_success = True

    def run(self, *args, **kwargs):
        from pilot.notifications.notify import notify_sync
        kwargs['desk'] = self.job_tracker.desk
        notify_sync(*args, **kwargs)


class SavedFilterImpactorModel(models.Model):
    impact_saved_filter = True

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(SavedFilterImpactorModel, self).save(*args, **kwargs)

        impact_saved_filter = self.impact_saved_filter
        # Never impact SavedFilter during a search vector update
        if getattr(self, 'updating_search_vector', False):
            impact_saved_filter = False

        if impact_saved_filter:
            schedule_notify_saved_filter(self)


def schedule_notify_saved_filter(instance):
    redis_client.sadd(
        NOTIFY_SAVED_FILTER_REDIS_KEY,
        f"{ContentType.objects.get_for_model(instance.__class__).id},{instance.id}"
    )


def run_notify_saved_filter():
    from pilot.notifications.feed import update_saved_filters_and_notify

    elements_to_update = []
    instances_by_desk = {}

    try:
        pipe_result = (
            redis_client.pipeline()
            .smembers(NOTIFY_SAVED_FILTER_REDIS_KEY)
            .delete(NOTIFY_SAVED_FILTER_REDIS_KEY)
            .execute()
        )
        elements_to_update = pipe_result[0]

        for element_to_update in elements_to_update:
            element_to_update = element_to_update.decode()
            content_type_id, instance_id = str(element_to_update).split(',')
            content_type = ContentType.objects.get_for_id(content_type_id)

            try:
                instance = content_type.get_object_for_this_type(id=instance_id)
            except ObjectDoesNotExist:
                logger.warning(
                    f"Deleted instance in run_saved_filter_notification (element_to_update={element_to_update})",
                    exc_info=True
                )

            instances_by_desk.setdefault(instance.desk, []).append(instance)

        for desk, updated_instances in instances_by_desk.items():
            update_saved_filters_and_notify(desk, updated_instances)
    except:
        logger.error(
            f"Error in run_saved_filter_notification (elements_to_update={elements_to_update})",
            exc_info=True
        )



