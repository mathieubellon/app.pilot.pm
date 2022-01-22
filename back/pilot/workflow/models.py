from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from pilot.desks.models import Desk
from pilot.utils.models import ChangeTrackingModel


class WorkflowState(ChangeTrackingModel):
    """ One state of a desk workflow """

    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='workflow_states'
    )

    label = models.CharField(
        verbose_name=_("Label"),
        max_length=200
    )

    order = models.PositiveSmallIntegerField(
        verbose_name=_("Ordre"),
    )

    color = models.CharField(
        verbose_name=_("Couleur"),
        max_length=7
    )

    class Meta:
        verbose_name = _('workflow state')
        verbose_name_plural = _('workflow states')
        ordering = ['order']

    def __str__(self):
        return self.label

    def get_absolute_url(self):
        return reverse('ui_workflow_states')
