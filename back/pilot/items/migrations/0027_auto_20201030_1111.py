# Generated by Django 2.2.14 on 2020-10-30 10:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0026_auto_20201019_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='editsession',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Créé le'),
        ),
        migrations.AlterField(
            model_name='editsession',
            name='updated_at',
            field=models.DateTimeField(blank=True, db_index=True, verbose_name='Mis à jour à'),
        ),
        migrations.AlterField(
            model_name='item',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Créé le'),
        ),
        migrations.AlterField(
            model_name='item',
            name='hidden',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Invisible'),
        ),
        migrations.AlterField(
            model_name='item',
            name='in_trash',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Mis à la corbeille'),
        ),
        migrations.AlterField(
            model_name='item',
            name='updated_at',
            field=models.DateTimeField(blank=True, db_index=True, verbose_name='Mis à jour à'),
        ),
    ]