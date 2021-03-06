# Generated by Django 2.2.14 on 2020-09-07 11:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0006_asset_folder'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assetright',
            options={'ordering': ('expiry',), 'verbose_name': "Droit d'utilisation de média"},
        ),
        migrations.RemoveField(
            model_name='asset',
            name='allowed_supports',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='copyright_duration',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='license',
        ),
        migrations.AlterField(
            model_name='assetright',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asset_rights', to='assets.Asset', verbose_name='Fichier'),
        ),
    ]
