# Generated by Django 2.1.7 on 2019-09-30 15:04

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0004_migrate_description_to_rte'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asset',
            name='description',
        ),
        migrations.RenameField(
            model_name='asset',
            old_name='new_description',
            new_name='description',
        ),
    ]
