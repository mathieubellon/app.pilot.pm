from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres import fields as pg_fields

from pilot.desks.models import Desk
from pilot.utils.models import ChangeTrackingModel


class Target(ChangeTrackingModel):
    """A marketing target."""

    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='targets'
    )

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

    class Meta:
        verbose_name = _('Cible')
        verbose_name_plural = _('Cibles')
        ordering = ['-created_at']

    def __str__(self):
        return self.name
