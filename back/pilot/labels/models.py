from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from pilot.desks.models import Desk
from pilot.utils.models import ChangeTrackingModel


class LabelTargetType:
    ASSET_RIGHT_MEDIUM = "asset_right_medium"
    ASSET_FOLDER = 'asset_folder'
    ASSET_TAGS = 'asset_tags'
    CHANNEL_TYPE = 'channel_type'
    ITEM_TAGS = 'item_tags'
    PROJECT_CATEGORY = 'project_category'
    PROJECT_PRIORITY = 'project_priority'
    PROJECT_TAGS = 'project_tags'

    CHOICES = [(target, target) for target in (
        ASSET_RIGHT_MEDIUM, ASSET_FOLDER, ASSET_TAGS, CHANNEL_TYPE, ITEM_TAGS,
        PROJECT_CATEGORY, PROJECT_PRIORITY, PROJECT_TAGS,
    )]


class Label(ChangeTrackingModel):
    """ One state of a desk workflow """

    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='labels'
    )

    name = models.CharField(
        verbose_name=_("Nom"),
        max_length=200
    )

    color = models.CharField(
        verbose_name=_("Couleur"),
        max_length=7
    )

    background_color = models.CharField(
        verbose_name=_("Couleur de fond"),
        max_length=7,
        blank=True
    )

    description = models.TextField(
        verbose_name=_("Description"),
        blank=True
    )

    target_type = models.CharField(
        verbose_name=_("Type de cible"),
        choices=LabelTargetType.CHOICES,
        max_length=100,
        blank=False,
        db_index=True
    )

    order = models.PositiveSmallIntegerField(
        verbose_name=_("Ordre"),
    )

    class Meta:
        verbose_name = _('label')
        ordering = ['order']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ui_labels_list')
