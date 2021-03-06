# Generated by Django 2.2.14 on 2020-10-19 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity_stream', '0003_auto_20200907_1317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='actor_identifier',
            field=models.CharField(blank=True, default='', max_length=63, verbose_name="Identifiant de l'utilisateur"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='activity',
            name='verb',
            field=models.CharField(choices=[('accepted_idea', 'Proposition acceptée'), ('asset_linked', 'Fichier lié'), ('asset_unlinked', 'Fichier retiré'), ('cancelled_rejection', 'a annulé le refus de la proposition'), ('closed', 'Clôture'), ('commented', 'Commentaire'), ('copied', 'Copie depuis'), ('created', 'Création'), ('deleted', 'Suppression'), ('feedback_approved', 'Contenu validé'), ('feedback_rejected', 'Contenu non validé'), ('frozen', 'Verrouillage édition'), ('hidden', 'Suppression'), ('joined_the_team', 'Nouvel utilisateur'), ('put_in_trash', 'Mis à la corbeille'), ('rejected_idea', 'Proposition rejetée'), ('reopened', 'Ré-ouverture'), ('restored', 'Restauration'), ('restored_from_trash', 'Restauration de la corbeille'), ('revoked', 'Révocation'), ('shared', 'Partage'), ('started_edit_session', "Session d'édition"), ('task_created', 'Création de tâche'), ('task_deleted', 'Suppression de tâche'), ('task_done', 'Tâche effectuée'), ('task_updated', 'Modification de tâche'), ('unfrozen', 'Déverrouillage édition'), ('updated', 'Modification'), ('updated_workflow', 'Statut de workflow modifié'), ('create_major_version', 'Version majeure créée'), ('accepted', 'a accepté'), ('approved', 'a approuvé'), ('did_not_validated', 'Rejet du partage'), ('merged_review', 'Intégration des modifications de'), ('published', 'a marqué [Publié]'), ('review_content_updated', 'Mise à jour du contenu partagé'), ('send_back_to_edition', 'a marqué [Brouillon]'), ('sent_for_approval', 'a partagé'), ('submitted_for_approval', 'a marqué [A Valider]'), ('saved_new_version', 'Nouvelle version'), ('send_to_publication', 'a marqué [A Publier]'), ('unpublished', 'a annulé la publication et marqué comme [Brouillon]'), ('unshared', 'a annulé le partage'), ('update_current_version', 'a mis à jour la version courante'), ('upgrade_major_version', 'Version majeure créée'), ('validated', 'Validation du partage')], db_index=True, max_length=100, verbose_name='Verbe'),
        ),
    ]
