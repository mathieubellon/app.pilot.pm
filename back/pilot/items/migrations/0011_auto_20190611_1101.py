# Generated by Django 2.1.7 on 2019-06-11 09:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0010_data_migration_for_realtime'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemsnapshot',
            name='content_schema',
        ),
        migrations.AlterField(
            model_name='itemsnapshot',
            name='item_type_snapshot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='item_types.ItemTypeSnapshot', verbose_name='Type de contenu'),
        ),
        migrations.AlterField(
            model_name='review',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='items.Item', verbose_name='Contenu'),
        ),
    ]