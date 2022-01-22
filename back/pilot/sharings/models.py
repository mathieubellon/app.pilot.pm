from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from pilot.channels.models import Channel
from pilot.desks.models import Desk
from pilot.items.models import Item
from pilot.itemsfilters.models import SavedFilter
from pilot.projects.models import Project
from pilot.utils.models import CreateTrackingModel, OptionalCreatorChangeTrackingModel
from pilot.utils.token_generator import generate_token


class SharingType:
    ITEM = 'item'
    PROJECT = 'project'
    CHANNEL = 'channel'
    LIST = 'list'
    CALENDAR = 'calendar'

    ALL_TYPES = (ITEM, PROJECT, CHANNEL, LIST, CALENDAR,)
    CHOICES = [(type, type) for type in ALL_TYPES]


class SharingStatus:
    APPROVED = 'approved'
    REJECTED = 'rejected'
    # EDITED is not in usage anymore, but were a thing for some monthes for the v4 release.
    EDITED = 'edited'

    CHOICES = (
        (APPROVED, _("Approuvé")),
        (REJECTED, _("Rejeté")),
        (EDITED, _("Edité")),
    )


def validate_sharing(sharing):
    # A deactivated doesn't have to be validated anymore
    if sharing.deactivated:
        return

    if sharing.type not in SharingType.ALL_TYPES:
        raise ValidationError(f"Sharing type must be one of {SharingType.ALL_TYPES}")

    if not sharing.email and sharing.is_editable:
        raise ValidationError(f"A sharing without email cannot be editable")

    if sharing.type == SharingType.ITEM and not sharing.item:
        raise ValidationError("Sharing of type 'item' should have an Item instance")
    if sharing.type == SharingType.PROJECT and not sharing.project:
        raise ValidationError("Sharing of type 'project' should have a Project instance")
    if sharing.type == SharingType.CHANNEL and not sharing.channel:
        raise ValidationError("Sharing of type 'channel' should have a Channel instance")
    if sharing.type == SharingType.LIST and not sharing.saved_filter:
        raise ValidationError("Sharing of type 'list' should have a SavedFilter instance")
    if sharing.type == SharingType.CALENDAR and not sharing.saved_filter:
        raise ValidationError("Sharing of type 'calendar' should have a SavedFilter instance")


class Sharing(CreateTrackingModel):
    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='sharings',
        null=True,  # May be null if deactivated
    )

    type = models.CharField(
        verbose_name=_("Type"),
        choices=SharingType.CHOICES,
        max_length=32,
        null=True,  # May be null if deactivated
    )

    token = models.CharField(
        verbose_name=_("Token"),
        max_length=255,
        db_index=True
    )

    email = models.EmailField(
        verbose_name=_("Email"),
        max_length=254,
        blank=True
    )

    password = models.CharField(
        verbose_name=_("Mot de passe"),
        max_length=254,
        blank=True,
        help_text=_("Un mot de passe (optionnel) pour protéger le partage.")
    )

    message = models.TextField(
        verbose_name=_("Message au destinataire"),
        blank=True
    )

    is_editable = models.BooleanField(
        verbose_name=_("Items editables"),
        default=False
    )

    deactivated = models.BooleanField(
        verbose_name=_("Accès désactivé"),
        default=False
    )

    # ===================
    # Single Item sharing
    # ===================

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name=_("Contenu"),
        related_name='sharings',
        null=True,
        blank=True
    )

    # ===================
    # Project's Item sharing
    # ===================

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name=_("Projet"),
        related_name='sharings',
        null=True,
        blank=True
    )

    # ===================
    # Channel's Item sharing
    # ===================

    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        verbose_name=_("Canal"),
        related_name='sharings',
        null=True,
        blank=True
    )

    # ===================
    # Saved Filter sharing ( list or calendar )
    # ===================

    saved_filter = models.ForeignKey(
        SavedFilter,
        on_delete=models.CASCADE,
        verbose_name=_("Saved filter"),
        related_name='sharings',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('Partage')
        verbose_name_plural = _('Partages')
        ordering = ['-created_at']

    def __str__(self):
        return _("Partage vers {}").format(self.email)

    def save(self, *args, **kwargs):
        validate_sharing(self)

        if not self.token:
            self.token = generate_token()
        # Ensure that `saved_filter` and `token` fields are unique together.
        while Sharing.objects.filter(token=self.token).exclude(pk=self.pk).exists():
            self.token = generate_token()
        super(Sharing, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return self.get_internal_absolute_url()

    def get_internal_absolute_url(self):
        """Returns the internal URL for this sharing"""
        if self.deactivated:
            return None
        return f"{self.get_target().get_absolute_url()}?showSharingsModal=1"

    def get_public_absolute_url(self):
        """Returns the public URL for this sharing"""
        if self.type == SharingType.ITEM:
            return reverse('ui_shared_item', kwargs={
                'item_pk': self.item_id,
                'token': self.token,
            })

        else:
            return reverse(
                'ui_sharing',
                kwargs={'token': self.token,}
            )

    def get_password_required_url(self):
        return reverse(
            'ui_sharing_password_required',
            kwargs={'token': self.token, }
        )

    def get_target(self):
        if self.deactivated:
            return None

        if self.type == SharingType.ITEM:
            return self.item
        if self.type == SharingType.PROJECT:
            return self.project
        if self.type == SharingType.CHANNEL:
            return self.channel
        if self.type in [SharingType.LIST, SharingType.CALENDAR]:
            return self.saved_filter

        # This should not happen because we validate the integrity of the data when we save()
        raise Exception("WTF ?")

    def get_query_string(self):
        """
        Get the query string to apply on the items API for this sharing.
        Should be used as well to restrict the visible items in the API ( see SharedApiMixin and PublicSharedItemRetrieve )
        """
        if self.deactivated:
            return None

        if self.type == SharingType.ITEM:
            return f'id={self.item_id}'
        if self.type == SharingType.PROJECT:
            return f'project={self.project_id}'
        if self.type == SharingType.CHANNEL:
            return f'channels={self.channel_id}'
        if self.type in [SharingType.LIST, SharingType.CALENDAR]:
            return self.saved_filter.query

        # This should not happen because we validate the integrity of the data when we save()
        raise Exception("WTF ?")


class ItemFeedback(models.Model):
    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='feedbacks'
    )

    sharing = models.ForeignKey(
        Sharing,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name=_("Contenu"),
        related_name='feedbacks'
    )

    status = models.CharField(
        verbose_name=_("Statut"),
        choices=SharingStatus.CHOICES,
        max_length=32
    )

    feedback_message = models.TextField(
        verbose_name=_("Commentaire de relecture"),
        blank=True
    )

    created_at = models.DateTimeField(
        verbose_name=_("Date de relecture"),
        default=timezone.now
    )

    class Meta:
        verbose_name = _('Feedback de contenu')

    def get_absolute_url(self):
        return self.sharing.get_absolute_url()
