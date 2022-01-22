# Generated by Django 2.1.7 on 2019-09-30 14:40

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0003_auto_20190801_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='new_description',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Description'),
        ),
    ]