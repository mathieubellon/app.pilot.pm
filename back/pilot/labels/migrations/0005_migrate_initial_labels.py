# Generated by Django 2.2.11 on 2020-07-28 06:59

from django.db import migrations


from pilot.utils import noop


def migrate_initial_labels(apps, schema_editor):
    Label = apps.get_model('labels', 'Label')

    Label.objects.filter(color='#34495e').update(color='#ECEFF1',background_color='#37474F')
    Label.objects.filter(color='#95a5a6').update(color='#263238',background_color='#CFD8DC')
    Label.objects.filter(color='#3B5998').update(color='#E8EAF6',background_color='#283593')
    Label.objects.filter(color='#4099FF').update(color='#E3F2FD',background_color='#1565C0')
    Label.objects.filter(color='#e74c3c').update(color='#FBE9E7',background_color='#D84315')

    Label.objects.filter(color='#ee4f4f').update(color='#FFEBEE',background_color='#C62828')
    Label.objects.filter(color='#ff9800').update(color='#FFF8E1',background_color='#FF8F00')
    Label.objects.filter(color='#cbd3d8').update(color='#263238',background_color='#CFD8DC')


class Migration(migrations.Migration):

    dependencies = [
        ('labels', '0004_auto_20200130_1057'),
    ]

    operations = [
        migrations.RunPython(migrate_initial_labels, noop),
    ]
