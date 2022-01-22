# Generated by Django 2.1.7 on 2019-04-08 09:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('itemsfilters', '0001_move_filter_models'),
    ]

    operations = [
        migrations.RenameField(
            model_name='savedfilter',
            old_name='filter',
            new_name='query',
        ),
        migrations.AlterField(
            model_name='savedfilter',
            name='query',
            field=models.TextField(verbose_name='Query string du filtre'),
        ),

        migrations.AddField(
            model_name='savedfilter',
            name='created_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='savedfilter_created', to=settings.AUTH_USER_MODEL, verbose_name='Créé par'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='savedfilter',
            name='updated_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Mis à jour à'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='savedfilter',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='savedfilter_updated', to=settings.AUTH_USER_MODEL, verbose_name='Mis à jour par'),
        ),




        migrations.AddField(
            model_name='publicsharedfilter',
            name='created_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='publicsharedfilter_created', to=settings.AUTH_USER_MODEL, verbose_name='Créé par'),
            preserve_default=False,
        ),
        migrations.RenameField(
            model_name='publicsharedfilter',
            old_name='item_saved_filter',
            new_name='saved_filter',
        ),
        migrations.AlterUniqueTogether(
            name='publicsharedfilter',
            unique_together={('saved_filter', 'token')},
        ),
    ]