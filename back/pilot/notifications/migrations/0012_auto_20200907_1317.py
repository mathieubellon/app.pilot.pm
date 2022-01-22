# Generated by Django 2.2.14 on 2020-09-07 11:17

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0011_migrate_comment_notifications'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('copy_project', 'copy_project'), ('export_desk', 'export_desk'), ('export_xls', 'export_xls'), ('feed_saved_filter', 'feed_saved_filter'), ('feed_activity', 'feed_activity'), ('internal_shared_filter', 'internal_shared_filter'), ('mention_comment', 'mention_comment'), ('mention_annotation', 'mention_annotation'), ('reminder', 'reminder'), ('task_assigned', 'task_assigned'), ('task_updated', 'task_updated'), ('task_todo', 'task_todo'), ('task_deleted', 'task_deleted'), ('validation_sharing', 'validation_sharing'), ('validation_idea', 'validation_idea')], db_index=True, max_length=100, verbose_name='Type de notification'),
        ),
        migrations.AlterField(
            model_name='notificationfeed',
            name='activity_verbs',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('accepted_idea', 'Proposition acceptée'), ('asset_linked', 'Fichier lié'), ('asset_unlinked', 'Fichier retiré'), ('cancelled_rejection', 'a annulé le refus de la proposition'), ('closed', 'Clôture'), ('commented', 'Commentaire'), ('copied', 'Copie depuis'), ('created', 'Création'), ('deleted', 'Suppression'), ('feedback_approved', 'Contenu validé'), ('feedback_rejected', 'Contenu non validé'), ('hidden', 'Suppression'), ('joined_the_team', 'Nouvel utilisateur'), ('put_in_trash', 'Mis à la corbeille'), ('rejected_idea', 'Proposition rejetée'), ('reopened', 'Ré-ouverture'), ('restored', 'Restauration'), ('restored_from_trash', 'Restauration de la corbeille'), ('revoked', 'Révocation'), ('shared', 'Partage'), ('started_edit_session', "Session d'édition"), ('task_created', 'Création de tâche'), ('task_deleted', 'Suppression de tâche'), ('task_done', 'Tâche effectuée'), ('task_updated', 'Modification de tâche'), ('updated', 'Modification'), ('updated_workflow', 'Statut de workflow modifié'), ('create_major_version', 'Version majeure créée')], max_length=100), blank=True, default=list, size=None),
        ),
    ]
