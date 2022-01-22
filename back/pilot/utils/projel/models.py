from cacheout import memoize
from django.contrib.postgres import fields as pg_fields
from django.db import models
from django.utils.translation import ugettext_lazy as _

from pilot.assets.models import Asset
from pilot.desks.models import Desk
from pilot.pilot_users.models import PilotUser
from pilot.utils import states
from pilot.utils.models import HideableModel, OptionalCreatorChangeTrackingModel
from pilot.utils.projel.managers import ActiveProjelManager, BaseProjelManager, ClosedProjelManager, IdeaProjelManager, \
    ProjelManager, UnconfirmedProjelManager
from pilot.utils.prosemirror.prosemirror import prosemirror_json_to_search_document
from pilot.utils.search import FullTextSearchModel


class Projel(FullTextSearchModel,
             OptionalCreatorChangeTrackingModel,
             HideableModel):
    """
    This is the base class for Project and Channel.
    The "Projel" word is the contraction of Project + Channel, and is proudly coined by TW :D
    """

    STATES_CHOICES = (
        (states.STATE_IDEA, _("Proposition")),
        (states.STATE_REJECTED, _("Rejeté")),
        (states.STATE_ACTIVE, _("Actif")),
        (states.STATE_CLOSED, _("Fermé")),
        (states.STATE_COPY, _("En cours de copie")),
    )

    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='%(class)ss'
    )

    # ===================
    # Content
    # ===================

    name = models.CharField(
        verbose_name=_("Nom"),
        max_length=200,
        db_index=True
    )

    # A rich-text field
    description = pg_fields.JSONField(
        verbose_name=_("Description"),
        default=dict,
        blank=True
    )

    # A rich-text field
    hierarchy = pg_fields.JSONField(
        verbose_name=_("Arborescence des contenus"),
        default=list,
        blank=True
    )

    # ===================
    # Related business objects
    # ===================

    owners = models.ManyToManyField(
        PilotUser,
        verbose_name=_("Responsables"),
        related_name='%(class)ss_by_owners',
        blank=True,
    )

    assets = models.ManyToManyField(
        Asset,
        verbose_name=_("Fichiers liés"),
        related_name='%(class)ss',
        blank=True
    )

    # ===================
    # State fields
    # ===================

    state = models.CharField(
        max_length=16,
        choices=STATES_CHOICES,
        blank=False,
        default=states.STATE_ACTIVE,
        verbose_name=_("Statut"),
        db_index=True
    )

    closed_at = models.DateTimeField(
        verbose_name=_("Fermé le"),
        blank=True,
        null=True
    )

    objects = ProjelManager()
    active_objects = ActiveProjelManager()
    closed_objects = ClosedProjelManager()
    idea_objects = IdeaProjelManager()
    unconfirmed_objects = UnconfirmedProjelManager()
    all_the_objects = BaseProjelManager()  # for django admin

    class Meta:
        abstract = True
        ordering = ['-created_at']
        # Django doc warn against using a base manager that filter out some results.
        # We do it anyway to filter out the hidden project/channels, because there's no other way
        # to filter them out from a DRF serialization.
        base_manager_name = 'objects'

    def __str__(self):
        return self.name

    @memoize(maxsize=1)
    def get_search_values(self):
        return [
            self.name,
            prosemirror_json_to_search_document(self.description)
        ]
