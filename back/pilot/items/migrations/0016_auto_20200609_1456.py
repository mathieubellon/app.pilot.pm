# Generated by Django 2.2.11 on 2020-06-09 12:56

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0015_init_last_editor'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='last_edition_datetime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Mise à jour du contenu à'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='item',
            name='history',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name="Historique d'édition"),
        ),
        migrations.AlterField(
            model_name='item',
            name='last_editor',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True, verbose_name='Dernier éditeur'),
        ),
    ]
