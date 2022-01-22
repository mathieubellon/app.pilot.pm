# Generated by Django 2.2.14 on 2020-10-30 10:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('list_config', '0002_listconfig_columns'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listconfig',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Créé le'),
        ),
        migrations.AlterField(
            model_name='listconfig',
            name='updated_at',
            field=models.DateTimeField(blank=True, db_index=True, verbose_name='Mis à jour à'),
        ),
    ]