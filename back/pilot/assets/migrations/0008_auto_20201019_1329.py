# Generated by Django 2.2.14 on 2020-10-19 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0007_auto_20200907_1317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='extension',
            field=models.CharField(blank=True, default='', max_length=500, verbose_name='Extension'),
            preserve_default=False,
        ),
    ]
