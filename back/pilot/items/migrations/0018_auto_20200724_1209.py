# Generated by Django 2.2.11 on 2020-07-24 10:09

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0017_init_last_edition_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='field_versions',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name="Versions d'édition des champs"),
        ),
        migrations.AlterField(
            model_name='itemsharing',
            name='status',
            field=models.CharField(choices=[('pending', 'En attente'), ('approved', 'Approuvé'), ('rejected', 'Rejeté'), ('edited', 'Edité')], default='pending', max_length=32, verbose_name='Statut'),
        ),
        migrations.CreateModel(
            name='ItemHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(max_length=500)),
                ('changes', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict), blank=True, default=list, size=None)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='items.Item')),
            ],
        ),
    ]