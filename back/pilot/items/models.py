import json
import logging

from cacheout import memoize
from django.utils.functional import cached_property, empty
from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.urls import reverse
from django.db import models, transaction
from django.db.models.expressions import Func, Value, F
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres import fields as pg_fields

from pilot.accounts.usage_limit import ItemUsageLimit
from pilot.assets.models import Asset
from pilot.channels.models import Channel
from pilot.desks.models import Desk
from pilot.items.managers import ActiveItemManager, BaseItemManager, InTrashItemManager, ItemManager
from pilot.labels.models import Label
from pilot.notifications.jobs import SavedFilterImpactorModel
from pilot.item_types.item_content_fields import content_schema_to_content_fields
from pilot.item_types.models import ItemType, ItemTypeSnapshot
from pilot.pilot_users.models import PilotUser
from pilot.projects.models import Project
from pilot.targets.models import Target
from pilot.utils.pilot_languages import LANGUAGES_CHOICES
from pilot.item_types.item_content import ItemContentMixin
from pilot.utils.models import HideableModel, OptionalCreatorChangeTrackingModel
from pilot.utils.prosemirror.prosemirror import prosemirror_json_to_search_document
from pilot.utils.search import FullTextSearchModel, TrigramIndex
from pilot.workflow.models import WorkflowState

logger = logging.getLogger(__name__)


class Item(ItemContentMixin,
           FullTextSearchModel,
           SavedFilterImpactorModel,
           OptionalCreatorChangeTrackingModel,
           HideableModel,
           models.Model):
    """An item."""

    NON_METADATA_FIELDS = (
        'json_content',
        'annotations',
        'updated_at',  # No need to store that, there's already a created_at on EditSession
        'history',  # History is not part of the metadata
        # Search fields doesn't need to be serialized
        'search_vector',
        'partial_search_document'
    )

    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='items'
    )

    # Auto incremented field based on the number of created items by desk.
    # Behaves as a primary key. See the save() method.
    number = models.PositiveSmallIntegerField(
        verbose_name=_("Nombre")
    )

    is_private = models.BooleanField(
        verbose_name=_("Contenu privé ?"),
        default=False,
        help_text=_("Ce contenu sera uniquement accessible par vous, "
                    "un administrateur ou un des responsables du contenu")
    )

    # ===================
    # Content
    # ===================

    item_type = models.ForeignKey(
        ItemType,
        on_delete=models.CASCADE,
        verbose_name=_("Type de contenu"),
        related_name='items'
    )

    annotations = pg_fields.JSONField(
        verbose_name=_("Annotations"),
        null=True,
        blank=True
    )

    field_versions = pg_fields.JSONField(
        verbose_name=_("Versions d'édition des champs"),
        default=dict,
        blank=True
    )

    # The last editor of the content ( not the metadata ), that may be an internal user (user_id) or external user (email)
    last_editor = pg_fields.JSONField(
        verbose_name=_("Dernier éditeur"),
        null=True
    )

    # The last edit datetime of the content ( not the metadata )
    last_edition_datetime = models.DateTimeField(
        verbose_name=_("Mise à jour du contenu à"),
        blank=True
    )

    # ===================
    # Related business objects
    # ===================

    owners = models.ManyToManyField(
        PilotUser,
        related_name='items',
        blank=True,
        verbose_name=_("Responsables")
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        verbose_name=_("Projets"),
        related_name='items',
        null=True,
        blank=True,
    )

    channels = models.ManyToManyField(
        Channel,
        verbose_name=_("Canaux"),
        related_name='items',
        blank=True,
    )

    targets = models.ManyToManyField(
        Target,
        verbose_name=_("Cibles"),
        related_name='items',
        blank=True,
    )

    assets = models.ManyToManyField(
        Asset,
        verbose_name=_("Fichiers liés"),
        related_name='items',
        blank=True,
    )

    master_translation = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        verbose_name=_("Traduction master"),
        related_name='translations',
        blank=True,
        null=True,
    )

    copied_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        verbose_name=_("Copié depuis"),
        blank=True,
        null=True
    )

    # ===================
    # Other metadata
    # ===================

    language = models.CharField(
        max_length=5,
        blank=True,
        choices=LANGUAGES_CHOICES,
        verbose_name=_("Langue du contenu"),
        db_index=True
    )

    tags = models.ManyToManyField(
        Label,
        verbose_name=_("Tags"),
        related_name="items_by_tags",
    )

    # ===================
    # State fields
    # ===================

    workflow_state = models.ForeignKey(
        WorkflowState,
        on_delete=models.SET_NULL,
        verbose_name=_("État de workflow"),
        related_name="items",
        null=True,
        blank=True,
    )

    in_trash = models.BooleanField(
        verbose_name=_("Mis à la corbeille"),
        default=False,
        db_index=True
    )

    # ===================
    # Freezing
    # ===================

    # The content cannot be edited while this is true
    frozen = models.BooleanField(
        verbose_name=_("Verrouillé"),
        default=False
    )

    frozen_at = models.DateTimeField(
        verbose_name=_("Verrouillé à"),
        blank=True,
        null=True
    )

    frozen_by = models.ForeignKey(
        PilotUser,
        on_delete=models.SET_NULL,
        related_name='freezed_items',
        verbose_name=_("Verrouillé par"),
        blank=True,
        null=True
    )

    # A rich-text field
    frozen_message = pg_fields.JSONField(
        verbose_name=_("Commentaire verrouillage"),
        default=dict,
        blank=True,
        null=True
    )

    class Meta:
        unique_together = ('desk', 'number')
        verbose_name = _('Contenu')
        verbose_name_plural = _('Contenus')
        ordering = ['-created_at']
        # Indexes doesn't seems to work on abstract classes ?!?
        # Maybe fixed in a later django release
        indexes = [
            # The index for full-text searches
            GinIndex(fields=['search_vector']),
            TrigramIndex(fields=['partial_search_document'])
        ]

    objects = ActiveItemManager()  # Only active items (visible, and not in trash)
    in_trash_objects = InTrashItemManager()
    accessible_objects = ItemManager()  # Item displayable in the UX : visible or in trash
    all_the_objects = BaseItemManager()  # for django admin

    creation_task_group_id = None

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.hidden:
            return None
        return reverse('ui_item_details', kwargs={'item_pk': self.pk, })

    def save(self, **kwargs):
        from pilot.tasks.initial_tasks import import_task_group_on_instance, init_publication_task_for_item
        is_creation = not self.pk
        publication_dt = self._publication_dt

        # In creation, ensure the subscription limit is not reached
        if is_creation:
            ItemUsageLimit(self.desk).check_limit()

        # Set an initial workflow_state if it's not set
        if is_creation and not self.workflow_state:
            self.workflow_state = self.desk.workflow_states.first()

        if not self.number:
            # Items are numbered in sequence by desk.
            # Each time an item is created, the ItemStats.items_created_num field is incremented by 1.
            # E.g.: if the item number #52 is deleted, the next created item on this desk will have the number #53.
            stats = ItemStats.objects.get_or_create(desk=self.desk)[0]
            stats.items_created_num += 1
            stats.save()
            self.number = stats.items_created_num

        self.clean_content()

        # Save the item and the session into a transaction to stay consistent
        with transaction.atomic():
            # Save the item normally
            super(Item, self).save(**kwargs)

            if is_creation:
                if publication_dt == empty:
                    publication_dt = None

                # Create the first version
                self.create_session(created_by_id=self.created_by_id)

                # During creation, we first check if there is an initial task group
                if self.creation_task_group_id:
                    import_task_group_on_instance(
                        linked_object=self,
                        task_group_id=self.creation_task_group_id,
                        user=self.created_by,
                        publication_dt=publication_dt
                    )
                # No initial task group, but a publication date : we must create an initial publication task
                elif publication_dt:
                    init_publication_task_for_item(self, publication_dt)
            elif publication_dt != empty:
                # Update publication task if it was set
                if self.publication_task:
                    self.publication_task.deadline = publication_dt
                    self.publication_task.save()
                # Else, create one
                else:
                    init_publication_task_for_item(self, publication_dt)

    @memoize(maxsize=1)
    def get_search_values(self):
        search_values = [self.title]
        for content_field in content_schema_to_content_fields(self.get_all_field_schema()):
            if content_field.is_prosemirror:
                search_values.append(prosemirror_json_to_search_document(self.content.get(content_field.name, '')))

        return search_values

    def create_session(self, timestamp=None, created_by_id=None, restored_from=None):
        if not timestamp:
            timestamp = timezone.now()
        # We don't use self.sessions.create() here,
        # because this method does not update the self.sessions internal cache,
        # and we need it to be up to date for serializing.
        session = EditSession.objects.create(
            item=self,
            created_by_id=created_by_id,
            item_type_snapshot=self.item_type.last_snapshot,
            start=timestamp,
            end=timestamp,
            content=self.content,
            annotations=self.annotations,
            restored_from=restored_from,
            editors=[created_by_id]
        )
        self.sessions.add(session)
        return session

    def restore_session(self, user, session):
        """
        Restore an item content to the state it was into a previous version
        """
        # Update the content and fields history
        for field_name, restored_value in session.content.items():
            if self.content.get(field_name) != restored_value:
                self.field_versions[field_name] += 1
                self.content[field_name] = restored_value

        self.updated_by = user
        self.annotations = session.annotations
        self.save()
        return self.create_session(created_by_id=user.id, restored_from=session)

    def create_major_version(self, user):
        """
        Create a new EditSession with a major version.

        The new major version will be identical to the current version.
        Can only be done if the previous version is not already a major version ( X.0 )
        """
        if self.last_session.minor_version == 0:
            raise ValidationError("Cannot create a major version because the current session is already a major version")

        session = self.create_session(created_by_id=user.id)
        session.major_version = session.major_version + 1
        session.minor_version = 0
        session.save()

    @cached_property
    def last_session(self):
        """
        Returns the most recent EditSession
        """
        try:
            return self.sessions.select_related('created_by', 'restored_from').latest()
        except EditSession.DoesNotExist:
            return None

    def get_content_schema_impl(self):
        """Returns the content schema for this Item."""
        return self.item_type.content_schema

    @cached_property
    def publication_task(self):
        # If the tasks has been select_related when querying the item,
        # then the cache in the related queryset is already filled
        # and we iterate on it to avoid hitting the db
        if self.tasks.all()._result_cache is not None:
            for task in self.tasks.all():
                if task.is_publication:
                    return task
        # No select_related, we query the db directly
        else:
            try:
                return self.tasks.get(is_publication=True)
            except ObjectDoesNotExist:
                return None

        return None

    # Use the 'empty' marker because None may be a valid value to reset to an null date
    _publication_dt = empty
    @property
    def publication_dt(self):
        # For creation and update, return the correct value to the serializer
        if self._publication_dt is not empty:
            return self._publication_dt

        return self.publication_task.deadline if self.publication_task else None

    @publication_dt.setter
    def publication_dt(self, _publication_dt):
        # Legacy API will set the publication_dt attribute.
        # It will then be used during Item.save() to update the publication task
        self._publication_dt = _publication_dt

    @property
    def author(self):
        return self.created_by.get_short_name() if self.created_by else ''


class EditSession(ItemContentMixin, OptionalCreatorChangeTrackingModel):
    """
    Represent a timeframe where users made some changes to an item content.
    The EditSession is closed after a period of inactivity ( BREAK_TIME_BETWEEN_SESSIONS ).
    We store the item content at the end of the EditSession.

    Each EditSession have a version.
    By default, the minor version is upgraded when a new session is created.
    It may be declared as a new major version instead by the user.
    """

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name=_("Contenu"),
        related_name='sessions'
    )

    item_type_snapshot = models.ForeignKey(
        ItemTypeSnapshot,
        on_delete=models.CASCADE,
        verbose_name=_("Type de contenu")
    )

    # A list of editors, that may be internal users (user_id) or external users (email)
    editors = pg_fields.JSONField(
        verbose_name=_("Editeurs"),
        default=list
    )

    start = models.DateTimeField(
        verbose_name=_("Début"),
        default=timezone.now
    )

    end = models.DateTimeField(
        verbose_name=_("Fin"),
        default=timezone.now
    )

    restored_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        verbose_name=_("Restauré à partir de"),
        null=True,
        blank=True
    )

    # Freeze the annotations at the time of the session
    annotations = pg_fields.JSONField(
        verbose_name=_("Annotations"),
        null=True,
        blank=True
    )

    major_version = models.IntegerField(
        verbose_name=_("Version majeure"),
        default=1
    )
    minor_version = models.IntegerField(
        verbose_name=_("Version mineure"),
        default=0
    )

    class Meta:
        get_latest_by = 'created_at'
        verbose_name = _("Version")
        verbose_name_plural = _("Versions")
        ordering = ['-major_version', '-minor_version', '-created_at']

    def __str__(self):
        return self.title

    objects = models.Manager()

    def save(self, *args, **kwargs):
        """
        When creating a new session, we upgrade the version.

        We upgrade the minor version by default.
        The user may upgrade the major version later.
        """
        # Creation
        if not self.pk:  # The version number should increment only when new instances are created.
            last_session = self.item.last_session
            # Don't do anything if we're the first session, the version will default to 1.0
            if last_session:
                # Always keep the current major version
                self.major_version = last_session.major_version
                # If the content has evolved, that means a new minor version
                self.minor_version = last_session.minor_version + 1

        super(EditSession, self).save(*args, **kwargs)

    @property
    def desk(self):
        return self.item.desk

    def get_content_schema_impl(self):
        """Returns the content schema for this EditSession."""
        return self.item_type_snapshot.content_schema

    @property
    def item_type(self):
        return self.item_type_snapshot.as_item_type()

    @property
    def version(self):
        """
        Property for backward-compatibility with the old single-versionning system
        """
        return "{}.{}".format(self.major_version, self.minor_version)

    def get_version_display(self):
        return "V{}".format(self.version)

    def get_absolute_url(self):
        return "{item_url}?showDiff={version}".format(
            item_url=reverse('ui_item_details', kwargs={'item_pk': self.item.id}),
            version=self.version
        )


class ItemStats(models.Model):
    """Collects Items statistics by desks."""

    desk = models.OneToOneField(
        Desk,
        verbose_name=_("Desk"),
        related_name='item_stats',
        on_delete=models.CASCADE
    )

    items_created_num = models.PositiveSmallIntegerField(
        verbose_name=_("Nombre de contenus créés"),
        default=0
    )

    class Meta:
        verbose_name = _('Items Stats')
        verbose_name_plural = _('Items Stats')

    def __str__(self):
        return "#{0}".format(self.items_created_num)
