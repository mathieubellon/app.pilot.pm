from django.contrib.postgres.indexes import GinIndex
from django.db.models import Count
from django.urls import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from pilot.accounts.usage_limit import ProjectUsageLimit
from pilot.channels.models import Channel
from pilot.labels.models import Label
from pilot.pilot_users.models import PilotUser
from pilot.targets.models import Target
from pilot.utils.projel.models import Projel
from pilot.workflow.models import WorkflowState

from pilot.utils.search import TrigramIndex


class Project(Projel):
    """A project"""

    # ===================
    # Content
    # ===================

    start = models.DateField(
        verbose_name=_("Date de début"),
        blank=True,
        null=True,
        db_index=True
    )

    end = models.DateField(
        verbose_name=_("Date de fin"),
        blank=True,
        null=True,
        db_index=True
    )

    # ===================
    # Related business objects
    # ===================

    channels = models.ManyToManyField(
        Channel,
        verbose_name=_("Canaux"),
        blank=True,
        related_name='projects'
    )

    members = models.ManyToManyField(
        PilotUser,
        verbose_name=_("Membres"),
        related_name='projects_by_members',
        blank=True
    )

    targets = models.ManyToManyField(
        Target,
        verbose_name=_("Cibles"),
        related_name='projects',
        blank=True,
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

    priority = models.ForeignKey(
        Label,
        on_delete=models.SET_NULL,
        verbose_name=_("Priorité"),
        related_name="projects_by_priority",
        blank=True,
        null=True,
    )

    category = models.ForeignKey(
        Label,
        on_delete=models.SET_NULL,
        verbose_name=_("Categorie"),
        related_name="projects_by_category",
        blank=True,
        null=True,
    )

    tags = models.ManyToManyField(
        Label,
        verbose_name=_("Tags"),
        related_name="projects_by_tags",
    )

    # ===================
    # External world fields
    # ===================

    created_by_external_email = models.EmailField(
        verbose_name=_("Créé par contact externe"),
        max_length=254,
        blank=True,
        db_index=True
    )

    created_by_external_token = models.CharField(
        verbose_name=_("Créé par token externe"),
        max_length=255,
        blank=True
    )

    class Meta:
        verbose_name = _('Projet')
        verbose_name_plural = _('Projets')
        # Indexes doesn't seems to work on abstract classes ?!?
        # Maybe fixed in a later django release
        indexes = [
            # The index for full-text searches
            GinIndex(fields=['search_vector']),
            TrigramIndex(fields=['partial_search_document'])
        ]

    def get_absolute_url(self):
        if self.hidden:
            return None

        return reverse('ui_project_detail', args=[self.pk])

    def save(self, *args, **kwargs):
        # In creation, ensure the subscription limit is not reached
        if not self.pk:
            ProjectUsageLimit(self.desk).check_limit()

        # Ensure the start date is always before the end date
        if self.start and self.end and self.start >= self.end:
            self.end, self.start = self.start, self.end

        super(Project, self).save(*args, **kwargs)

    def get_progress(self):
        workflow_states = (
            WorkflowState.objects
            .filter(items__project=self, items__in_trash=False)
            .order_by('order')
            .only('label', 'color')
            .annotate(items_count=Count('items'))
        )

        return [
            {
                'label': workflow_state.label,
                'color': workflow_state.color,
                'occurences': workflow_state.items_count
            }
            for workflow_state
            in workflow_states
        ]
