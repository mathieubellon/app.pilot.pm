# Generated by Django 2.2.14 on 2020-10-05 13:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0010_init_hierarchy'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channel',
            name='level',
        ),
        migrations.RemoveField(
            model_name='channel',
            name='lft',
        ),
        migrations.RemoveField(
            model_name='channel',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='channel',
            name='rght',
        ),
        migrations.RemoveField(
            model_name='channel',
            name='tree_id',
        ),
    ]
