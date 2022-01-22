# Generated by Django 2.2.14 on 2020-09-07 11:17

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('item_types', '0006_itemtype_icon_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemtype',
            name='with_significant_time',
        ),
        migrations.AlterField(
            model_name='itemtype',
            name='content_schema',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, verbose_name='Schema'),
        ),
        migrations.AlterField(
            model_name='itemtype',
            name='icon_name',
            field=models.CharField(blank=True, max_length=100, verbose_name="Nom d'icône"),
        ),
        migrations.AlterField(
            model_name='itemtype',
            name='metadata_schema',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, verbose_name='Schema des metadata'),
        ),
    ]