from django.urls import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.indexes import GinIndex

from pilot.labels.models import Label
from pilot.utils.projel.models import Projel
from pilot.utils.search import TrigramIndex


class Channel(Projel):
    """A channel."""

    # ===================
    # Related business objects
    # ===================

    type = models.ForeignKey(
        Label,
        on_delete=models.SET_NULL,
        verbose_name=_("Type"),
        related_name="channels_by_type",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('Canal')
        verbose_name_plural = _('Canaux')
        # Indexes doesn't seems to work on abstract classes ?!?
        # Maybe fixed in a later django release
        indexes = [
            # The index for full-text searches
            GinIndex(fields=['search_vector']),
            TrigramIndex(fields=['partial_search_document'])
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if self.hidden:
            return None
        return reverse('ui_channel_detail', args=[self.pk])


