# Generated by Django 2.2.11 on 2020-07-24 12:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0019_migrate_item_history'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='history',
        ),
    ]