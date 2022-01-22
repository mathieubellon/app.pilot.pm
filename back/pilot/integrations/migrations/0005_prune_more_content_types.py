# Generated by Django 2.2.14 on 2020-11-24 09:04

from django.db import migrations

from pilot.utils import noop

def prune_content_types(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.filter(model='projecttransitionlog').delete()
    ContentType.objects.filter(model='itemtransitionlog').delete()
    ContentType.objects.filter(model='itemsharing').delete()
    ContentType.objects.filter(model='channeltoken').delete()
    ContentType.objects.filter(model='twittercredential').delete()
    ContentType.objects.filter(model='itemcustomtype').delete()
    ContentType.objects.filter(model='forkedcontentversion').delete()
    ContentType.objects.filter(model='facebookcredential').delete()
    ContentType.objects.filter(model='itemvisibilitytransitionlog').delete()
    ContentType.objects.filter(model='annotationmigrationfailure').delete()
    ContentType.objects.filter(model='channeltype').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0004_auto_20201030_1111'),
    ]

    operations = [
        migrations.RunPython(prune_content_types, noop),
    ]