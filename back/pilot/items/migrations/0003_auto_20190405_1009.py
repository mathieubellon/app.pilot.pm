# Generated by Django 2.1.7 on 2019-04-05 08:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0002_auto_20190221_1506'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='copied_from',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='items.Item', verbose_name='Copié depuis'),
        ),
        migrations.AlterField(
            model_name='itemsnapshot',
            name='restored_from',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='items.ItemSnapshot', verbose_name='Restauré à partir de'),
        ),
    ]
