# Generated by Django 2.2.11 on 2020-05-19 14:29
from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations

from pilot.utils import noop


def migrate_comment_notifications(apps, schema_editor):
    Notification = apps.get_model("notifications", "Notification")
    Comment = apps.get_model("comments", "Comment")

    for notification in Notification.objects.filter(type__startswith='mention_').iterator():
        comment_id = notification.data.get('comment_id')
        comment_data = {
            'id': comment_id
        }

        try:
            comment = Comment.objects.get(id=comment_id)
            comment_data['comment_content'] = comment.comment_content
        except ObjectDoesNotExist:
            pass

        notification.data = {
            'comment': comment_data
        }
        notification.save()


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0010_migrate_notification_types'),
    ]

    operations = [
        migrations.RunPython(migrate_comment_notifications, reverse_code=noop),
    ]
