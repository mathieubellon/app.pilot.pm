# Generated by Django 2.1.7 on 2019-07-29 10:05

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('desks', '0001_rebirth'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('user_email', models.EmailField(blank=True, max_length=254)),
                ('comment', models.TextField(verbose_name='comment')),
                ('submit_date', models.DateTimeField(db_index=True, default=None, verbose_name='date/time submitted')),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(default=dict, verbose_name='Data')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('desk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='desks.Desk', verbose_name='Desk')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
