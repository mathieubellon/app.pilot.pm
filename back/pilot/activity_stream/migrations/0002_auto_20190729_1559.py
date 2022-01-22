# Generated by Django 2.1.7 on 2019-07-29 13:59

import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity_stream', '0001_rebirth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='action_object_object_id',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='diff',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='target_object_id',
            field=models.PositiveIntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='verb',
            field=models.CharField(choices=[('accepted_idea', 'Proposition acceptée'), ('asset_linked', 'Fichier lié'), ('asset_unlinked', 'Fichier retiré'), ('cancelled_rejection', 'a annulé le refus de la proposition'), ('closed', 'Clôture'), ('commented', 'Commentaire'), ('copied', 'Copie depuis'), ('created', 'Création'), ('deleted', 'Suppression'), ('hidden', 'Suppression'), ('joined_the_team', 'Nouvel utilisateur'), ('put_in_trash', 'Mis à la corbeille'), ('rejected_idea', 'Proposition rejetée'), ('reopened', 'Ré-ouverture'), ('restored', 'Restauration'), ('restored_from_trash', 'Restauration de la corbeille'), ('review_content_updated', 'Mise à jour du contenu partagé'), ('revoked', 'Révocation'), ('shared', 'Partage'), ('started_edit_session', "Session d'édition"), ('task_created', 'Création de tâche'), ('task_deleted', 'Suppression de tâche'), ('task_done', 'Tâche effectuée'), ('task_updated', 'Modification de tâche'), ('updated', 'Modification'), ('updated_workflow', 'Statut de workflow modifié'), ('upgrade_major_version', 'Version majeure créée'), ('accepted', 'a accepté'), ('approved', 'a approuvé'), ('did_not_validated', 'Rejet du partage'), ('merged_review', 'Intégration des modifications de'), ('published', 'a marqué [Publié]'), ('send_back_to_edition', 'a marqué [Brouillon]'), ('sent_for_approval', 'a partagé'), ('submitted_for_approval', 'a marqué [A Valider]'), ('saved_new_version', 'Nouvelle version'), ('send_to_publication', 'a marqué [A Publier]'), ('unpublished', 'a annulé la publication et marqué comme [Brouillon]'), ('unshared', 'a annulé le partage'), ('update_current_version', 'a mis à jour la version courante'), ('validated', 'Validation du partage')], db_index=True, max_length=100, verbose_name='Verbe'),
        ),
    ]