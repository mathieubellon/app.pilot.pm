from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from pilot.desks.models import Desk
from pilot.pilot_users.models import PilotUser
from pilot.utils.models import NonErasingGenericForeignKey


class Favorite(models.Model):
    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='favorites'
    )

    user = models.ForeignKey(
        PilotUser,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )

    target_object_id = models.PositiveIntegerField()

    target = NonErasingGenericForeignKey('target_content_type', 'target_object_id')

    @property
    def target_name(self):
        if hasattr(self.target, 'title'):
            return self.target.title
        elif hasattr(self.target, 'name'):
            return self.target.name
        else:
            return ''

    @property
    def target_url(self):
        return self.target.get_absolute_url()
