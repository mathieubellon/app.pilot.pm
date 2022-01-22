# Generated by Django 2.1.7 on 2019-06-20 10:09

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('item_types', '0005_auto_20190611_1030'),
        ('items', '0011_auto_20190611_1101'),
    ]

    operations = [

        migrations.RenameField(
            model_name="Review",
            old_name='item_snapshot',
            new_name='session'
        ),

        migrations.RenameModel(
            old_name='ItemSnapshot',
            new_name='EditSession'
        ),
        migrations.RenameModel(
            old_name='Review',
            new_name='ItemSharing'
        ),

    ]
