# Generated by Django 2.1.7 on 2019-09-30 14:50

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0005_migrate_description_to_rte'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channel',
            name='description',
        ),
        migrations.RenameField(
            model_name='channel',
            old_name='new_description',
            new_name='description',
        ),
    ]