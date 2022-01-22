# Generated by Django 2.1.7 on 2020-02-07 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0003_comment_new_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='deletion_date',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='date/time deleted'),
        ),
        migrations.AddField(
            model_name='comment',
            name='edition_date',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='date/time edited'),
        ),
    ]
