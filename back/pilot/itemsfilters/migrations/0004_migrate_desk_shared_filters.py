# Generated by Django 2.1.7 on 2019-04-08 13:08

from django.db import migrations
from django.utils import timezone

from pilot.utils import noop


def migrate_desk_shared_filters(apps, schema_editor):
    SavedFilter = apps.get_model('itemsfilters', 'SavedFilter')
    now = timezone.now()

    for saved_filter in SavedFilter.objects.filter(is_desk_shared=True):
        for user in saved_filter.desk.users.exclude(id=saved_filter.user_id):
            # Create a new saved filter with the same data, but on all the other users of the desk
            saved_filter.id = None
            saved_filter.user = user
            saved_filter.created_by = user
            saved_filter.created_at = now
            saved_filter.updated_by = user
            saved_filter.updated_at = now
            saved_filter.save()


class Migration(migrations.Migration):

    dependencies = [
        ('itemsfilters', '0003_init_creators'),
    ]

    operations = [
        migrations.RunPython(migrate_desk_shared_filters, noop),
    ]