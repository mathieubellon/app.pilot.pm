from django.db import migrations, models
from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.utils.timezone

from pilot.utils import noop


def update_contentypes(apps, schema_editor):
    """
    Updates content types.
    We want to have the same content type id, when the model is moved and renamed.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    db_alias = schema_editor.connection.alias

    qs = ContentType.objects.using(db_alias).filter(app_label='items', model='itemsavedfilter')
    qs.update(app_label='itemsfilters', model='savedfilter')

    qs = ContentType.objects.using(db_alias).filter(app_label='items', model='itemsharedfilter')
    qs.update(app_label='itemsfilters', model='publicsharedfilter')


class Migration(migrations.Migration):

    dependencies = [
        # We need to run 0002_rename_table form app1 first,
        # because it changes the table of ModelThatShouldBeMoved.
        # Only after that we will update content types and rename the model.
        ('items', '0004_rename_filter_models'),
    ]

    state_operations = [
         migrations.CreateModel(
            name='ItemSavedFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Titre')),
                ('filter', models.TextField(verbose_name='Filtre')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Créé le')),
                ('type', models.CharField(choices=[('calendar', 'Calendrier'), ('list', 'Liste')], default='calendar', max_length=30, verbose_name='Type')),
                ('is_desk_shared', models.BooleanField(default=False, verbose_name="Disponible pour toute l'équipe")),
                ('is_sliding_calendar', models.BooleanField(default=True)),
                ('display_tasks', models.BooleanField(default=True)),
                ('display_projects', models.BooleanField(default=False)),
                ('display_all_tasks', models.BooleanField(default=False)),
                ('notification_feed_instance_ids', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), default=list, size=None, verbose_name='Champ technique pour le NotificationFeed')),
                ('desk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_items_filters', to='desks.Desk', verbose_name='Desk')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_items_filters', to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur')),
            ],
            options={
                'verbose_name': 'Item Saved Filter',
                'verbose_name_plural': 'Items Saved Filters',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ItemSharedFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(help_text='Envoyer à cette adresse (une seule)', max_length=254, verbose_name='Email')),
                ('password', models.CharField(blank=True, help_text="Un mot de passe (optionnel) pour protéger le calendrier (sera indiqué dans l'email avec l'url de partage", max_length=254, verbose_name='Mot de passe')),
                ('token', models.CharField(max_length=255, verbose_name='Token')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Créé le')),
                ('items_locked', models.BooleanField(default=False, help_text='Les contenus dans le calendrier ne seront pas cliquables si cette case est cochée', verbose_name='Contenus verrouillés')),
                ('item_saved_filter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sharings', to='itemsfilters.ItemSavedFilter', verbose_name='Saved filter')),
            ],
            options={
                'verbose_name': 'Item Shared Filter',
                'verbose_name_plural': 'Items Shared Filters',
                'ordering': ['-created_at'],
            },
        ),

        migrations.RenameModel(
            old_name='ItemSavedFilter',
            new_name='SavedFilter',
        ),

        migrations.RenameModel(
            old_name='ItemSharedFilter',
            new_name='PublicSharedFilter',
        ),

        migrations.AlterUniqueTogether(
            name='PublicSharedFilter',
            unique_together={('item_saved_filter', 'token')},
        ),
    ]

    database_operations = [
        migrations.RunPython(update_contentypes, noop),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations,
            database_operations=database_operations
        ),
    ]
