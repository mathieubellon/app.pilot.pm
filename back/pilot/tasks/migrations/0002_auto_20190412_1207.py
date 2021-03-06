# Generated by Django 2.1.7 on 2019-04-12 10:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_rebirth'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='task_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks_new', to='tasks.TaskGroup', verbose_name='Groupe de tâche'),
        ),
        migrations.AlterField(
            model_name='task',
            name='name',
            field=models.TextField(blank=True, verbose_name='Nom'),
        ),
        migrations.AlterField(
            model_name='taskgroup',
            name='tasks',
            field=models.ManyToManyField(related_name='task_group_old', to='tasks.Task', verbose_name='Tâches'),
        ),
    ]
