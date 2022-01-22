from django.db.models import TextField
from django.db.models.functions import Cast

from pilot.comments.models import Comment
from pilot.items.models import Item
from pilot.pilot_users.models import PilotUser, Team
from pilot.queue.jobs import Job
from pilot.queue import jobs_registar
from pilot.queue.rq_setup import medium_priority_queue
from pilot.utils.prosemirror.prosemirror import for_each_mentions


class MentionUpdateJob(Job):
    job_type = jobs_registar.JOB_TYPE_MENTION_UPDATE
    queue = medium_priority_queue

    def run(self, instance):
        if isinstance(instance, PilotUser):
            new_name = instance.username
            uid = f'mention-user-{instance.id}'
        elif isinstance(instance, Team):
            new_name = instance.name
            uid = f'mention-team-{instance.id}'
        else:
            raise Exception("Incorrect instance in MentionUpdateJob, should be either a User or a Team")

        comments = Comment.objects.annotate(
            search=Cast('comment_content', TextField()),
        ).filter(search__contains=uid)

        for comment in comments.iterator():
            self.replace_for_uid(comment.comment_content, uid, new_name)
            comment.save()

        items = Item.objects.annotate(
            search=Cast('annotations', TextField()),
        ).filter(search__contains=uid)

        for item in items.iterator():
            for annotations in item.annotations.values():
                for annotation in annotations.values():
                    self.replace_for_uid(annotation, uid, new_name)
            item.prevent_updated_at = True
            item.save()

    def replace_for_uid(self, comment_content, uid, new_name):
        def do_replace(node, mention):
            if mention['uid'] == uid:
                node['text'] = '@' + new_name

        for_each_mentions(comment_content, do_replace)
