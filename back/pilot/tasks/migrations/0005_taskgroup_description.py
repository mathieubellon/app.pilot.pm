# Generated by Django 2.1.7 on 2019-05-14 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_auto_20190412_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskgroup',
            name='description',
            field=models.CharField(blank=True, max_length=500, verbose_name='Description'),
        ),
    ]
