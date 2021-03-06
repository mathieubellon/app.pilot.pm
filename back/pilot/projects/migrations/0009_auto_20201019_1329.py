# Generated by Django 2.2.14 on 2020-10-19 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_init_hierarchy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='state',
            field=models.CharField(choices=[('idea', 'Proposition'), ('rejected', 'Rejeté'), ('active', 'Actif'), ('closed', 'Fermé'), ('copy', 'En cours de copie')], db_index=True, default='active', max_length=16, verbose_name='Statut'),
        ),
    ]
