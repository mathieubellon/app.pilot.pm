# Generated by Django 2.1.7 on 2019-02-14 10:25

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    replaces = [('item_types', '0001_initial'), ('item_types', '0002_move_custom_item_type'), ('item_types', '0003_auto_20180320_1703'), ('item_types', '0004_auto_20180320_1724'), ('item_types', '0005_auto_20180321_1403'), ('item_types', '0006_migrate_builtin_item_type'), ('item_types', '0007_auto_20180329_1251'), ('item_types', '0008_auto_20180329_1520'), ('item_types', '0009_migrate_existing_schemas'), ('item_types', '0010_auto_20180514_1028'), ('item_types', '0011_auto_20180605_0927'), ('item_types', '0012_init_media_item_type')]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('desks', '0001_rebirth'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(blank=True, verbose_name='Mis à jour à')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Créé le')),
                ('name', models.CharField(max_length=500, verbose_name='Nom')),
                ('description', models.CharField(blank=True, max_length=500, verbose_name='Description')),
                ('content_schema', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Schema')),
                ('metadata_schema', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Schema des metadata')),
                ('with_significant_time', models.BooleanField(default=False, verbose_name="Utiliser l'heure sur l'échéance de publication ?")),
                ('hidden', models.BooleanField(default=False, verbose_name='Invisible')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itemtype_created', to=settings.AUTH_USER_MODEL, verbose_name='Créé par')),
                ('desk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_types', to='desks.Desk', verbose_name='Desk')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='itemtype_updated', to=settings.AUTH_USER_MODEL, verbose_name='Mis à jour par')),
            ],
            options={
                'verbose_name': 'Type de contenu',
                'verbose_name_plural': 'Types de contenu',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ItemTypeSnapshot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Créé le')),
                ('serialized_data', django.contrib.postgres.fields.jsonb.JSONField(default=dict, verbose_name='ItemType serialized data')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itemtypesnapshot_created', to=settings.AUTH_USER_MODEL, verbose_name='Créé par')),
                ('item_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='snapshots', to='item_types.ItemType', verbose_name='Type de contenu')),
            ],
            options={
                'verbose_name': 'Snapshot type de contenu',
                'verbose_name_plural': 'Snapshots types de contenu',
                'ordering': ('-created_at',),
            },
        ),
    ]