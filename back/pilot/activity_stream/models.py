import logging

from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres import fields as pg_fields

from pilot.channels.models import Channel
from pilot.desks.models import Desk
from pilot.items.models import Item
from pilot.itemsfilters.models import SavedFilter
from pilot.pilot_users.models import PilotUser
from pilot.projects.models import Project
from pilot.utils.models import NonErasingGenericForeignKey

logger = logging.getLogger(__name__)


class ActivityManager(models.Manager):
    def get_permited_activities(self, desk, user):
        if not user.permissions.is_restricted_editor:
            return super(ActivityManager, self).get_queryset().filter(desk=desk)

        # Else, restrict the visible activities
        permitted_activities = []

        def add_activities_for_content_type(content_type, permitted_pks):
            permitted_activities.extend(Activity.objects.filter(
                desk=desk,
                target_content_type=content_type,
                target_object_id__in=permitted_pks
            ).values_list('id', flat=True))

        # Get objects restricted user has access to
        permitted_items = list(
            Item
            .accessible_objects
            .filter(desk=desk)
            .filter_by_permissions(user)
            .values_list('pk', flat=True)

        )

        permitted_projects = list(
            Project
            .objects
            .filter(desk=desk)
            .filter_by_permissions(user)
            .values_list('pk', flat=True)
        )

        permitted_channels = list(
            Channel
            .objects
            .filter(desk=desk)
            .filter_by_permissions(user)
            .values_list('pk', flat=True)
        )

        # Get the activities related to the items
        item_content_type = ContentType.objects.get_for_model(Item)
        add_activities_for_content_type(item_content_type, permitted_items)

        # Get the activities related to the projects
        project_content_type = ContentType.objects.get_for_model(Project)
        add_activities_for_content_type(project_content_type, permitted_projects)

        # Get the activities related to the channels
        channel_content_type = ContentType.objects.get_for_model(Channel)
        add_activities_for_content_type(channel_content_type, permitted_channels)

        return super(ActivityManager, self).get_queryset().filter(desk=desk, id__in=permitted_activities)


class Activity(models.Model):
    """
    Activity Stream.
    http://activitystrea.ms/specs/atom/1.0/
    """

    VERB_ACCEPTED_IDEA = 'accepted_idea'
    VERB_ASSET_LINKED = 'asset_linked'
    VERB_ASSET_UNLINKED = 'asset_unlinked'
    VERB_CANCELLED_REJECTION = 'cancelled_rejection'
    VERB_CLOSED = 'closed'
    VERB_COMMENTED = 'commented'
    VERB_COPIED = 'copied'
    VERB_CREATED = 'created'
    VERB_DELETED = 'deleted'
    VERB_FEEDBACK_APPROVED = 'feedback_approved'
    VERB_FEEDBACK_REJECTED = 'feedback_rejected'
    VERB_FROZEN = 'frozen'
    VERB_HIDDEN = 'hidden'
    VERB_JOINED_TEAM = 'joined_the_team'
    VERB_PUT_IN_TRASH = 'put_in_trash'
    VERB_REJECTED_IDEA = 'rejected_idea'
    VERB_REOPENED = 'reopened'
    VERB_RESTORED = 'restored'
    VERB_RESTORED_FROM_TRASH = 'restored_from_trash'
    VERB_REVOKED = 'revoked'
    VERB_SHARED = 'shared'
    VERB_STARTED_EDIT_SESSION = 'started_edit_session'
    VERB_TASK_CREATED = 'task_created'
    VERB_TASK_DELETED = 'task_deleted'
    VERB_TASK_DONE = 'task_done'
    VERB_TASK_UPDATED = 'task_updated'
    VERB_UNFROZEN = 'unfrozen'
    VERB_UPDATED = 'updated'
    VERB_UPDATED_WORKFLOW = 'updated_workflow'
    VERB_CREATE_MAJOR_VERSION = 'create_major_version'

    ACTIVE_VERB_CHOICES = (
        (VERB_ACCEPTED_IDEA, _("Proposition acceptée")),
        (VERB_ASSET_LINKED, _("Fichier lié")),
        (VERB_ASSET_UNLINKED, _("Fichier retiré")),
        (VERB_CANCELLED_REJECTION, _("a annulé le refus de la proposition")),
        (VERB_CLOSED, _("Clôture")),
        (VERB_COMMENTED, _("Commentaire")),
        (VERB_COPIED, _("Copie depuis")),
        (VERB_CREATED, _("Création")),
        (VERB_DELETED, _("Suppression")),
        (VERB_FEEDBACK_APPROVED, _("Contenu validé")),
        (VERB_FEEDBACK_REJECTED, _("Contenu non validé")),
        (VERB_FROZEN, _("Verrouillage édition")),
        (VERB_HIDDEN, _("Suppression")),
        (VERB_JOINED_TEAM, _("Nouvel utilisateur")),
        (VERB_PUT_IN_TRASH, _("Mis à la corbeille")),
        (VERB_REJECTED_IDEA, _("Proposition rejetée")),
        (VERB_REOPENED, _("Ré-ouverture")),
        (VERB_RESTORED, _("Restauration")),
        (VERB_RESTORED_FROM_TRASH, _("Restauration de la corbeille")),
        (VERB_REVOKED, _("Révocation")),
        (VERB_SHARED, _("Partage")),
        (VERB_STARTED_EDIT_SESSION, _("Session d'édition")),
        (VERB_TASK_CREATED, _("Création de tâche")),
        (VERB_TASK_DELETED, _("Suppression de tâche")),
        (VERB_TASK_DONE, _("Tâche effectuée")),
        (VERB_TASK_UPDATED, _("Modification de tâche")),
        (VERB_UNFROZEN, _("Déverrouillage édition")),
        (VERB_UPDATED, _("Modification")),
        (VERB_UPDATED_WORKFLOW, _("Statut de workflow modifié")),
        (VERB_CREATE_MAJOR_VERSION, _("Version majeure créée")),
    )

    # Not created anymore, but kept to display the old Activity. Could be migrated.
    DEPRECATED_VERB_CHOICES = (
        ('accepted', _("a accepté")),
        ('approved', _("a approuvé")),
        ('did_not_validated', _("Rejet du partage")),
        ('merged_review', _("Intégration des modifications de")),
        ('published', _("a marqué [Publié]")),
        ('review_content_updated', _("Mise à jour du contenu partagé")),
        ('send_back_to_edition', _("a marqué [Brouillon]")),
        ('sent_for_approval', _("a partagé")),
        ('submitted_for_approval', _("a marqué [A Valider]")),
        ('saved_new_version', _("Nouvelle version")),
        ('send_to_publication', _("a marqué [A Publier]")),
        ('unpublished', _("a annulé la publication et marqué comme [Brouillon]")),
        ('unshared', _("a annulé le partage")),
        ('update_current_version', _("a mis à jour la version courante")),
        ('upgrade_major_version', _("Version majeure créée")),
        ('validated', _("Validation du partage")),
    )

    VERB_CHOICES = ACTIVE_VERB_CHOICES + DEPRECATED_VERB_CHOICES

    SYSTEM_USER = _("Pilot robot")
    PUBLIC_API_USER = _("Public API user")
    NON_DB_USERS = (SYSTEM_USER, PUBLIC_API_USER)

    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='activity_stream'
    )

    # The user that performed the activity.
    actor = models.ForeignKey(
        PilotUser,
        on_delete=models.SET_NULL,
        related_name='actor',
        blank=True,
        null=True
    )

    # Email of the user that performed the activity if no object is provided.
    actor_email = models.EmailField(
        verbose_name=_("Email de l'utilisateur"),
        max_length=254,
        blank=True
    )
    # Name of actor that are neither in db nor have an eal (e.g system for management command)
    actor_identifier = models.CharField(
        verbose_name=_("Identifiant de l'utilisateur"),
        max_length=63,
        blank=True
    )
    # The verb phrase that identifies the action of the activity.
    verb = models.CharField(
        verbose_name=_("Verbe"),
        choices=VERB_CHOICES,
        max_length=100,
        db_index=True
    )

    # The main object where the action were taken : Item, Project, Asset, Channel.
    # Should generally be set.
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='target',
        blank=True,
        null=True,
        db_index=True
    )
    target_object_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        db_index=True
    )
    target = NonErasingGenericForeignKey('target_content_type', 'target_object_id')

    # The string representation of the target, used after deletion
    target_str = models.CharField(
        max_length=5000,
        blank=True
    )

    # Optionnal.
    # The actual object where the action has been taken may be different from the target.
    # When this is the case, store it here.
    # Example : A ChannelToken on a Channel. A Task on an Item
    action_object_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='action_object',
        blank=True,
        null=True,
        db_index=True
    )
    # Todo : why is this field not a PositiveIntegerField ?
    action_object_object_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True
    )
    action_object = NonErasingGenericForeignKey('action_object_content_type', 'action_object_object_id')

    # The string representation of the action object, used after deletion
    action_object_str = models.CharField(
        max_length=5000,
        blank=True
    )

    created_at = models.DateTimeField(
        default=timezone.now
    )

    diff = pg_fields.JSONField(
        blank=True,
        null=True,
        encoder=DjangoJSONEncoder
    )

    objects = ActivityManager()

    class Meta:
        verbose_name = _('Activity')
        verbose_name_plural = _('Activities')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Creation
        if not self.pk:
            if self.target and not self.target_str:
                self.target_str = self.generate_target_str()

            if self.action_object and not self.action_object_str:
                action_object_display = self.generate_action_object_str()
                if len(action_object_display) > 1000:
                    action_object_display = action_object_display[:1000]
                self.action_object_str = action_object_display

        super(Activity, self).save(*args, **kwargs)

    @property
    def is_comment(self):
        return self.verb == Activity.VERB_COMMENTED

    def get_actor_display(self):
        if self.actor:
            return self.actor.username
        if self.actor_email:
            return self.actor_email
        if self.actor_identifier:
            return self.actor_identifier
        return ''

    def generate_target_str(self):
        target = self.target
        if not target:
            return ''

        instance_type = target._meta.verbose_name
        target_repr = force_text(target)

        if isinstance(target, SavedFilter):
            instance_type = _("Calendrier :") if target.type == 'calendar' else _("Liste de contenus :")

        return f"{instance_type} : {target_repr}"

    def generate_action_object_str(self):
        return f'{self.action_object}' if self.action_object else ''
