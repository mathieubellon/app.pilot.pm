# Generated by Django 2.2.11 on 2020-06-09 12:56

from django.db import migrations, models

from pilot.utils import noop


def init_last_edition_date(apps, schema_editor):
    Item = apps.get_model("items", "Item")
    Item.objects.update(last_edition_datetime=models.F('updated_at'))


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0016_auto_20200609_1456'),
    ]

    operations = [
        migrations.RunPython(init_last_edition_date, reverse_code=noop),
    ]