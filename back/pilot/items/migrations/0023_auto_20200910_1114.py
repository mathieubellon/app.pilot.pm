# Generated by Django 2.2.14 on 2020-09-10 09:14

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('items', '0022_auto_20200907_1317'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='frozen',
            field=models.BooleanField(default=False, verbose_name='Verrouillé'),
        ),
        migrations.AddField(
            model_name='item',
            name='frozen_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Verrouillé à'),
        ),
        migrations.AddField(
            model_name='item',
            name='frozen_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='freezed_items', to=settings.AUTH_USER_MODEL, verbose_name='Verrouillé par'),
        ),
        migrations.AddField(
            model_name='item',
            name='frozen_message',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, verbose_name='Commentaire verrouillage'),
        ),
    ]
