# Generated by Django 2.2.14 on 2020-11-24 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0013_init_html_fields'),
        ('wiki', '0002_init_wiki_home_pages'),
    ]

    operations = [
        migrations.AddField(
            model_name='wikipage',
            name='assets',
            field=models.ManyToManyField(blank=True, related_name='wiki_pages', to='assets.Asset', verbose_name='Fichiers liés'),
        ),
    ]
