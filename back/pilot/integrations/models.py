from django.utils.translation import ugettext_lazy as _
from django.db import models

from pilot.desks.models import Desk
from pilot.utils.models import ChangeTrackingModel
from pilot.utils.token_generator import generate_token


class ApiToken(ChangeTrackingModel):
    """
    API authorization token model.
    """
    token = models.CharField(
        verbose_name=_("Token"),
        max_length=200,
        unique=True
    )

    name = models.CharField(
        verbose_name=_("Nom"),
        max_length=600,
        blank=True
    )

    description = models.TextField(
        verbose_name=_("Description"),
        blank=True
    )

    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='api_tokens'
    )

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = generate_token()
        return super(ApiToken, self).save(*args, **kwargs)

    def __str__(self):
        return f"<ApiToken: {self.token} >"
