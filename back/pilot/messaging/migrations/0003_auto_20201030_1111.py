# Generated by Django 2.2.14 on 2020-10-30 10:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0002_auto_20200907_1317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='created_at',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Créé le'),
        ),
    ]
