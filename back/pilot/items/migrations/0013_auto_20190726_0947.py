# Generated by Django 2.1.7 on 2019-07-26 07:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0012_auto_20190620_1209'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='editsession',
            options={'get_latest_by': 'created_at', 'ordering': ['-major_version', '-minor_version', '-created_at'], 'verbose_name': 'Version', 'verbose_name_plural': 'Versions'},
        ),
        migrations.AddField(
            model_name='item',
            name='master_translation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='translations', to='items.Item', verbose_name='Traduction master'),
        ),
        migrations.AlterField(
            model_name='editsession',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='editsession_created', to=settings.AUTH_USER_MODEL, verbose_name='Créé par'),
        ),
        migrations.AlterField(
            model_name='editsession',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='items.Item', verbose_name='Contenu'),
        ),
        migrations.AlterField(
            model_name='editsession',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='editsession_updated', to=settings.AUTH_USER_MODEL, verbose_name='Mis à jour par'),
        ),
        migrations.AlterField(
            model_name='itemsharing',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itemsharing_created', to=settings.AUTH_USER_MODEL, verbose_name='Créé par'),
        ),
        migrations.AlterField(
            model_name='itemsharing',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sharings', to='items.Item', verbose_name='Contenu'),
        ),
        migrations.AlterField(
            model_name='itemsharing',
            name='session',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sharings', to='items.EditSession', verbose_name='Version du contenu'),
        ),
        migrations.AlterField(
            model_name='itemsharing',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='itemsharing_updated', to=settings.AUTH_USER_MODEL, verbose_name='Mis à jour par'),
        ),
    ]