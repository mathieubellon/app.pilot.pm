from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres import fields as pg_fields

from pilot.desks.models import Desk
from pilot.pilot_users.models import PilotUser
from pilot.utils.models import ChangeTrackingModel


class ListConfig(ChangeTrackingModel):
    """ One state of a desk workflow """

    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='list_configs'
    )

    name = models.CharField(
        verbose_name=_("Nom"),
        max_length=200
    )

    ordering = models.CharField(
        verbose_name=_("Tri"),
        max_length=200,
        blank=True
    )

    columns = pg_fields.JSONField(
        verbose_name=_("Colonnes"),
        default=dict,
        blank=True,
    )

    class Meta:
        verbose_name = _('List Config')
        unique_together = ('desk', 'name')

    def __str__(self):
        return self.name
