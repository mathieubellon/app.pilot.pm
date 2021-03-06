# Generated by Django 2.1.7 on 2019-02-14 10:29

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import pilot.utils.search


class Migration(migrations.Migration):

    replaces = [('items', '0001_initial'), ('items', '0002_auto_20150922_1755'), ('items', '0003_auto_20151119_0941'), ('items', '0004_auto_20151124_1630'), ('items', '0005_auto_20151214_1609'), ('items', '0006_auto_20151215_1602'), ('items', '0007_auto_20160126_1015'), ('items', '0008_itemsharedfilter_items_locked'), ('items', '0009_add_item_state_dates'), ('items', '0010_migrate_publication_date'), ('items', '0011_auto_20160331_1307'), ('items', '0012_migrate_item_state_dates'), ('items', '0013_migrate_item_state_dates_part_2'), ('items', '0014_item_builtin_item_type'), ('items', '0015_auto_20160511_1639'), ('items', '0016_remove_item_item_type'), ('items', '0017_rename_title_and_content'), ('items', '0018_rename_item_custom_type_schema'), ('items', '0019_itemcustomtype_schema'), ('items', '0020_migrate_itemcustomtype_schema'), ('items', '0021_setdefault_title_and_content_for_existing_schema'), ('items', '0022_migrate_itemcontent_raw_data'), ('items', '0023_rename_content_to_body'), ('items', '0024_item__raw_data'), ('items', '0025_item_annotations'), ('items', '0026_copy_item_content_and_annotations_from_latest_version'), ('items', '0027_auto_rename_raw_data_to_raw_content'), ('items', '0028_auto_rename_ContentVErsion_to_ItemSnapshot'), ('items', '0029_store_content_schema_on_snapshots'), ('items', '0030_init_content_schema_on_snapshots'), ('items', '0031_auto_20160531_1608'), ('items', '0032_change_item_versionning'), ('items', '0033_auto_20160601_1603'), ('items', '0034_auto_20160601_1622'), ('items', '0035_init_last_snapshot_metadata'), ('items', '0036_fix_markdown'), ('items', '0037_rename_old_annotations'), ('items', '0038_create_new_annotations_fields'), ('items', '0039_annotationmigrationfailure'), ('items', '0040_migrate_annotations_to_prosemirror'), ('items', '0041_migrate_markdown_to_json_20160808_1634'), ('items', '0042_review_refactorisation_20160909_1802'), ('items', '0043_migrate_item_snapshaot_add_item_type_auto_20161121_1223'), ('items', '0044_item_mapping'), ('items', '0045_convert_snapshot_annotations_to_jsonb'), ('items', '0046_annotation_repositionning'), ('items', '0047_naming_altering'), ('items', '0048_add_item_is_private'), ('items', '0049_auto_20170523_0943'), ('items', '0050_split_item_state'), ('items', '0051_migrate_item_list_saved_filter'), ('items', '0052_remove_item_state'), ('items', '0053_migrate_state_in_snapshot_metadata'), ('items', '0054_itemcustomtype_metadata_schema'), ('items', '0055_harmonie_mutuelle_emailing_item_type'), ('items', '0056_auto_20170623_1521'), ('items', '0057_remove_preset_tags_from_item_snapshot'), ('items', '0058_auto_20170627_1531'), ('items', '0059_auto_20170627_1538'), ('items', '0060_migrate_item_content_from_hstore_to_json'), ('items', '0061_auto_20170918_1452'), ('items', '0062_init_search_fields'), ('items', '0063_init_search_indicies'), ('items', '0064_migrate_content_schema_format'), ('items', '0065_auto_20171117_1344'), ('items', '0066_auto_20171117_1515'), ('items', '0067_auto_20171120_1134'), ('items', '0068_migrate_item_idea_content'), ('items', '0069_auto_20171127_1047'), ('items', '0070_init_custom_item_type_translations'), ('items', '0071_add_linked_items'), ('items', '0072_clean_item_type_fields'), ('items', '0073_remove_item_custom_type'), ('items', '0074_auto_20180329_2325'), ('items', '0075_migrate_item_mapping'), ('items', '0076_auto_20180423_1430'), ('items', '0077_auto_20180423_1726'), ('items', '0078_auto_20180423_1758'), ('items', '0079_auto_20180424_1741'), ('items', '0080_auto_20180426_1113'), ('items', '0081_migrate_campaign_to_project_in_item_saved_filter'), ('items', '0082_auto_20180613_0955'), ('items', '0083_auto_20180926_1038'), ('items', '0084_migrate_item_states'), ('items', '0085_auto_20181001_1358'), ('items', '0086_itemsavedfilter_is_sliding_calendar'), ('items', '0087_auto_20181105_1119'), ('items', '0088_init_saved_filter_instance_ids'), ('items', '0089_item_new_tags'), ('items', '0090_auto_20181129_1110')]

    initial = True

    dependencies = [
        ('item_types', '0001_rebirth'),
        ('targets', '0001_rebirth'),
        ('projects', '0001_rebirth'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('desks', '0001_rebirth'),
        ('labels', '0001_rebirth'),
        ('channels', '0001_rebirth'),
        ('assets', '0001_rebirth'),
        ('workflow', '0001_rebirth'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnotationMigrationFailure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('publication_dt', models.DateField(null=True)),
                ('state', models.TextField(blank=True)),
                ('error_message', models.TextField(blank=True)),
                ('pos_before', django.contrib.postgres.fields.jsonb.JSONField(blank=True)),
                ('text_before', models.TextField(blank=True)),
                ('pos_after', django.contrib.postgres.fields.jsonb.JSONField(blank=True)),
                ('text_after', models.TextField(blank=True)),
                ('comment_text', models.TextField(blank=True)),
                ('resolved', models.BooleanField(default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('desk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='desks.Desk')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(blank=True, verbose_name='Mis ?? jour ??')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Cr???? le')),
                ('search_vector', django.contrib.postgres.search.SearchVectorField(null=True)),
                ('partial_search_document', models.TextField(blank=True)),
                ('json_content', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Content data')),
                ('number', models.PositiveSmallIntegerField(verbose_name='Nombre')),
                ('explicit_name', models.CharField(blank=True, max_length=500, verbose_name='Nom explicite')),
                ('is_private', models.BooleanField(default=False, help_text='Ce contenu sera uniquement accessible par vous, un administrateur ou un des responsables du contenu', verbose_name='Contenu priv?? ?')),
                ('annotations', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True, verbose_name='Annotations')),
                ('mappings', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True, verbose_name='Mappings')),
                ('language', models.CharField(blank=True, choices=[('ar', 'Arabe'), ('bg_BG', 'Bulgare'), ('cs_CZ', 'Tch??que'), ('da_DK', 'Danois'), ('de_DE', 'Allemand'), ('el_GR', 'Grec'), ('en_US', 'Anglais'), ('es_ES', 'Espagnol'), ('et_EE', 'Estonien'), ('fi_FI', 'Finnois'), ('fr_FR', 'Fran??ais'), ('hr_HR', 'Japonais'), ('hu_HU', 'Hongrois'), ('it_IT', 'Italien'), ('lt_LT', 'Lituanien'), ('ja_JA', 'Japonais'), ('nl_NL', 'N??erlandais'), ('no_NO', 'Norv??gien'), ('pl_PL', 'Polonais'), ('pt_PT', 'Portugais'), ('ro_RO', 'Roumain'), ('ru_RU', 'Russe'), ('sk_SK', 'Slovaque'), ('sl_SI', 'Slov??ne'), ('sv_SE', 'Su??dois'), ('tr_TR', 'Turc'), ('zh_CN', 'Chinois')], db_index=True, max_length=5, null=True, verbose_name='Langue du contenu')),
                ('in_trash', models.BooleanField(default=False, verbose_name='Mis ?? la corbeille')),
                ('hidden', models.BooleanField(default=False, verbose_name='Invisible')),
                ('created_by_external_email', models.EmailField(blank=True, max_length=254, verbose_name='Cr???? par email externe')),
                ('created_by_external_token', models.CharField(blank=True, max_length=255, verbose_name='Cr???? par token externe')),
                ('external_publication_error', models.TextField(blank=True, max_length=511, null=True, verbose_name='Erreur de publication externe')),
                ('guidelines', models.TextField(blank=True, help_text="De quoi s'agit-il ? Description d??taill??e de la demande", verbose_name='Quoi et Qui')),
                ('where', models.TextField(blank=True, help_text='Informations relatives au lieu concern?? par la demande, le cas ??ch??ant', null=True, verbose_name='O??')),
                ('goal', models.TextField(blank=True, help_text='Valorisation de la marque, .. etc', null=True, verbose_name='Objectif de communication')),
                ('contacts', models.TextField(blank=True, help_text='Utiles au lecteur, ?? faire appara??tre dans le contenu final', null=True, verbose_name='Contacts')),
                ('sources', models.TextField(blank=True, help_text='Internes/externes, utiles pour la r??daction du contenu', null=True, verbose_name='Sources')),
                ('scope', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'R??gionale'), (1, 'Nationale'), (2, 'Internationale')], null=True, verbose_name='Port??e')),
                ('available_pictures', models.BooleanField(default=False, verbose_name='Photos disponibles')),
                ('photographer_needed', models.BooleanField(default=False, verbose_name='Envoyer un photographe sur place ?')),
                ('photo_investigations_needed', models.BooleanField(default=False, verbose_name='Recherches n??cessaires ?')),
                ('investigations_needed', models.BooleanField(default=False, verbose_name='Recherches documentaires n??cessaires ?')),
                ('support_needed', models.BooleanField(default=False, verbose_name='Soutien r??dactionnel n??cessaire ?')),
                ('assets', models.ManyToManyField(blank=True, related_name='items', to='assets.Asset', verbose_name='Fichiers li??s')),
                ('channel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='channels.Channel', verbose_name='Canal')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='item_created', to=settings.AUTH_USER_MODEL, verbose_name='Cr???? par')),
                ('desk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='desks.Desk', verbose_name='Desk')),
                ('item_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='item_types.ItemType', verbose_name='Type de contenu')),
                ('linked_items', models.ManyToManyField(blank=True, related_name='_item_linked_items_+', to='items.Item', verbose_name='Contenus li??s')),
                ('owners', models.ManyToManyField(blank=True, related_name='items', to=settings.AUTH_USER_MODEL, verbose_name='Responsables')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='projects.Project', verbose_name='Projets')),
                ('tags', models.ManyToManyField(related_name='items_by_tags', to='labels.Label', verbose_name='Tags')),
                ('targets', models.ManyToManyField(blank=True, related_name='items', to='targets.Target', verbose_name='Cibles')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='item_updated', to=settings.AUTH_USER_MODEL, verbose_name='Mis ?? jour par')),
                ('workflow_state', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='workflow.WorkflowState', verbose_name='??tat de workflow')),
            ],
            options={
                'verbose_name': 'Contenu',
                'verbose_name_plural': 'Contenus',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ItemSavedFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Titre')),
                ('filter', models.TextField(verbose_name='Filtre')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Cr???? le')),
                ('type', models.CharField(choices=[('calendar', 'Calendrier'), ('list', 'Liste')], default='calendar', max_length=30, verbose_name='Type')),
                ('is_desk_shared', models.BooleanField(default=False, verbose_name="Disponible pour toute l'??quipe")),
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
                ('email', models.EmailField(help_text='Envoyer ?? cette adresse (une seule)', max_length=254, verbose_name='Email')),
                ('password', models.CharField(blank=True, help_text="Un mot de passe (optionnel) pour prot??ger le calendrier (sera indiqu?? dans l'email avec l'url de partage", max_length=254, verbose_name='Mot de passe')),
                ('token', models.CharField(max_length=255, verbose_name='Token')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Cr???? le')),
                ('items_locked', models.BooleanField(default=False, help_text='Les contenus dans le calendrier ne seront pas cliquables si cette case est coch??e', verbose_name='Contenus verrouill??s')),
                ('item_saved_filter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sharings', to='items.ItemSavedFilter', verbose_name='Saved filter')),
            ],
            options={
                'verbose_name': 'Item Shared Filter',
                'verbose_name_plural': 'Items Shared Filters',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ItemSnapshot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Cr???? le')),
                ('json_content', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Content data')),
                ('content_schema', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, verbose_name='Schema')),
                ('comment', models.TextField(blank=True, verbose_name='Commentaire')),
                ('annotations', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True, verbose_name='Annotations')),
                ('annotations_migration_failure', models.BooleanField(default=False)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(default=dict, verbose_name='Metadata')),
                ('major_version', models.IntegerField(default=1, verbose_name='Version majeure')),
                ('minor_version', models.IntegerField(default=0, verbose_name='Version mineure')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itemsnapshot_created', to=settings.AUTH_USER_MODEL, verbose_name='Cr???? par')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='snapshots', to='items.Item', verbose_name='Contenu')),
                ('restored_from', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='items.ItemSnapshot', verbose_name='Restaur?? ?? partir de')),
            ],
            options={
                'verbose_name': 'Version',
                'verbose_name_plural': 'Versions',
                'ordering': ['-created_at'],
                'get_latest_by': 'created_at',
            },
        ),
        migrations.CreateModel(
            name='ItemStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('items_created_num', models.PositiveSmallIntegerField(default=0, verbose_name='Nombre de contenus cr????s')),
                ('desk', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='item_stats', to='desks.Desk', verbose_name='Desk')),
            ],
            options={
                'verbose_name': 'Items Stats',
                'verbose_name_plural': 'Items Stats',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(blank=True, verbose_name='Mis ?? jour ??')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Cr???? le')),
                ('json_content', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='Content data')),
                ('comment', models.TextField(blank=True, verbose_name='Commentaire')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('token', models.CharField(max_length=255, verbose_name='Token')),
                ('password', models.CharField(blank=True, help_text='Un mot de passe (optionnel) pour prot??ger la demande.', max_length=254, verbose_name='Mot de passe')),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('approved', 'Approuv??'), ('rejected', 'Rejet??')], default='pending', max_length=32, verbose_name='Statut')),
                ('review_comment', models.TextField(blank=True, verbose_name='Commentaire du relecteur')),
                ('reviewed_at', models.DateTimeField(blank=True, null=True, verbose_name='Vu le')),
                ('is_editable', models.BooleanField(default=False, verbose_name='Autoriser le destinataire ?? modifier le contenu')),
                ('has_fork', models.BooleanField(default=False, verbose_name='Le contact a modifi?? la copie envoy??e pour relecture')),
                ('is_merged', models.BooleanField(default=False, verbose_name='Le contenu est fusionn?? avec la version courante')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_created', to=settings.AUTH_USER_MODEL, verbose_name='Cr???? par')),
                ('item_snapshot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='items.ItemSnapshot', verbose_name='Version du contenu')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='review_updated', to=settings.AUTH_USER_MODEL, verbose_name='Mis ?? jour par')),
            ],
            options={
                'verbose_name': 'Partage',
                'verbose_name_plural': 'Partages',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='annotationmigrationfailure',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='annotation_migration_failures', to='items.Item'),
        ),
        migrations.AlterUniqueTogether(
            name='itemsharedfilter',
            unique_together={('item_saved_filter', 'token')},
        ),
        migrations.AddIndex(
            model_name='item',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_vector'], name='items_item_search__776677_gin'),
        ),
        migrations.AddIndex(
            model_name='item',
            index=pilot.utils.search.TrigramIndex(fields=['partial_search_document'], name='items_item_partial_afd5f8_gin'),
        ),
        migrations.AlterUniqueTogether(
            name='item',
            unique_together={('desk', 'number')},
        ),
    ]
