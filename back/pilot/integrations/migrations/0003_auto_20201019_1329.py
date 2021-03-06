# Generated by Django 2.2.14 on 2020-10-19 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0002_prune_content_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apitoken',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='Description'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='apitoken',
            name='name',
            field=models.CharField(blank=True, default='', max_length=600, verbose_name='Nom'),
            preserve_default=False,
        ),
    ]
