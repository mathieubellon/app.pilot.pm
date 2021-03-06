# Generated by Django 2.1.7 on 2019-03-18 13:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('desks', '0001_rebirth'),
        ('labels', '0002_asset_right_medium'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assets', '0001_rebirth'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetRight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(blank=True, verbose_name='Mis à jour à')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Créé le')),
                ('expiry', models.DateField(blank=True, null=True, verbose_name="Date d'expiration")),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asset_rights', to='assets.Asset', verbose_name='Asset')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assetright_created', to=settings.AUTH_USER_MODEL, verbose_name='Créé par')),
                ('desk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asset_rights', to='desks.Desk', verbose_name='Desk')),
                ('medium', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='asset_rights_by_medium', to='labels.Label', verbose_name='Support de communication')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assetright_updated', to=settings.AUTH_USER_MODEL, verbose_name='Mis à jour par')),
            ],
            options={
                'verbose_name': "Droit d'utilisation de média",
            },
        ),
    ]
