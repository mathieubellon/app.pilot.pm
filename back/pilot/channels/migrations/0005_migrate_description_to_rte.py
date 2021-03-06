# Generated by Django 2.1.7 on 2019-09-24 08:01

from django.db import migrations

from pilot.utils import noop
from pilot.utils.prosemirror.prosemirror import convert_text_to_prosemirror_doc


def migrate_description_to_rte(apps, schema_editor):
    Channel = apps.get_model('channels', 'Channel')

    for channel in Channel.objects.iterator():
        channel.new_description = convert_text_to_prosemirror_doc(channel.description)
        channel.save()


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0004_channel_new_description'),
    ]

    operations = [
        migrations.RunPython(migrate_description_to_rte, noop),
    ]
