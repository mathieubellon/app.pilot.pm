from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres import fields as pg_fields

from pilot.pilot_users.models import PilotUser
from pilot.utils.models import CreateTrackingModel


class Message(CreateTrackingModel, models.Model):
    MESSAGE_TYPE_RELEASE = 'release'
    MESSAGE_TYPE_DOWNTIME = 'downtime'

    MESSAGE_TYPE_CHOICES = (
        (MESSAGE_TYPE_RELEASE, _('Release')),
        (MESSAGE_TYPE_DOWNTIME, _('Downtime')),
    )

    name = models.CharField(
        verbose_name=_("Nom"),
        max_length=200,
        blank=True,
        help_text=_("Usage interne uniquement, non affiché aux utilisateurs")
    )

    users = models.ManyToManyField(
        PilotUser,
        verbose_name=_("Users"),
        related_name='messages',
        through='UserMessage'
    )

    type = models.CharField(
        verbose_name=_("Type de message"),
        choices=MESSAGE_TYPE_CHOICES,
        max_length=100,
        blank=True
    )

    # The textual content of the message, stored as a dict with translations :
    # { "fr": "...", "en": "..." }
    content = pg_fields.JSONField(
        verbose_name=_("Content"),
        default=dict,
        blank=True
    )

    def __str__(self):
        return self.name

    def send(self, to_users):
        for user in to_users:
            UserMessage.objects.create(
                user=user,
                message=self
            )


class UserMessage(models.Model):
    user = models.ForeignKey(
        PilotUser,
        on_delete=models.CASCADE,
        related_name='user_message_set'
    )

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='user_message_set'
    )

    read_at = models.DateTimeField(
        verbose_name=_("Lu le"),
        null=True
    )

    @property
    def is_read(self):
        return self.read_at is not None
