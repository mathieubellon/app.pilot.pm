from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields as pg_fields

from pilot.desks.models import Desk
from pilot.pilot_users.models import PilotUser
from pilot.utils.models import NonErasingGenericForeignKey


class Comment(models.Model):
    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='comments'
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content_object = NonErasingGenericForeignKey()

    user = models.ForeignKey(
        PilotUser,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        null=True
    )

    user_email = models.EmailField(
        blank=True
    )

    # A rich-text field
    comment_content = pg_fields.JSONField(
        verbose_name=_("Commentaire"),
        default=dict
    )

    submit_date = models.DateTimeField(
        default=None,
        db_index=True,
        verbose_name=_('date/time submitted'),
    )

    edition_date = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_('date/time edited'),
    )

    deletion_date = models.DateTimeField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_('date/time deleted')
    )

    # Additionnal arbitrary data the notification creator wish to store in the db
    data = pg_fields.JSONField(
        verbose_name=_("Data"),
        default=dict
    )

    def save(self, *args, **kwargs):
        if self.submit_date is None:
            self.submit_date = timezone.now()
        super(Comment, self).save(*args, **kwargs)

    @property
    def is_deleted(self):
        return bool(self.deletion_date)
