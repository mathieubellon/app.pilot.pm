# Generated by Django 2.2.14 on 2020-09-07 11:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0021_auto_20200625_1443'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='mappings',
        ),
        migrations.RemoveField(
            model_name='itemsharing',
            name='has_fork',
        ),
        migrations.RemoveField(
            model_name='itemsharing',
            name='is_merged',
        ),
        migrations.RemoveField(
            model_name='itemsharing',
            name='session',
        ),
    ]
