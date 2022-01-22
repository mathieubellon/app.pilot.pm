from pilot.utils.prosemirror.prosemirror import EMPTY_PROSEMIRROR_DOC
from pilot.queue.jobs import Job
from pilot.queue import jobs_registar
from pilot.queue.rq_setup import medium_priority_queue


class ItemTypeUpdateJob(Job):
    job_type = jobs_registar.JOB_TYPE_ITEM_TYPE_UPDATE
    queue = medium_priority_queue

    def run(self, item_type, field_names_to_wipe, new_prosemirror_field_names):
        for item in item_type.items.all():
            item.content = {field_name:content for field_name, content in item.content.items()
                            if field_name not in field_names_to_wipe}
            for new_prosemirror_field_name in new_prosemirror_field_names:
                item.content[new_prosemirror_field_name] = EMPTY_PROSEMIRROR_DOC
            item.prevent_updated_at = True
            item.save()
