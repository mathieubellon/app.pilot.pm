import logging

from django.urls import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres import fields as pg_fields

from pilot.desks.models import Desk
from pilot.pilot_users.models import PilotUser
from pilot.utils.models import CreateTrackingModel, ChangeTrackingModel
from pilot.utils.token_generator import generate_token

logger = logging.getLogger(__name__)


class SavedFilter(ChangeTrackingModel, models.Model):
    """
    A saved custom filter for items.

    Item() querysets can be filtered dynamically via django-filter.
    The filter is based on the value provided in the query string, e.g.:
    ?start=2013-09-29&end=2013-11-10&project=2

    The `query` field stores this raw query string without the question mark
    which is not considered as a part of the query string.
    """

    TYPE_CALENDAR = 'calendar'
    TYPE_LIST = 'list'

    TYPE_CHOICES = (
        (TYPE_CALENDAR, _("Calendrier")),
        (TYPE_LIST, _("Liste")),
    )

    PERIOD_24_HOURS = 24
    PERIOD_WEEK_IN_HOURS = 24 * 7
    PERIOD_MONTH_IN_HOURS = 24 * 31
    PERIOD_QUARTER_IN_HOURS = 24 * 31 * 3

    # The allowed values for the `period` param in the query string.
    PERIOD_CHOICES = (  # In hours.
        ('', _("Période")),
        (PERIOD_24_HOURS, _("Prochaines 24h")),
        (PERIOD_WEEK_IN_HOURS, _("7 prochains jours")),
        (PERIOD_MONTH_IN_HOURS, _("30 prochains jours")),
        (PERIOD_QUARTER_IN_HOURS, _("90 prochains jours")),
    )

    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='saved_items_filters'
    )

    user = models.ForeignKey(
        PilotUser,
        on_delete=models.CASCADE,
        verbose_name=_("Utilisateur"),
        related_name='saved_items_filters'
    )

    title = models.CharField(
        verbose_name=_("Titre"),
        max_length=255,
        db_index=True
    )

    query = models.TextField(
        verbose_name=_("Query string du filtre")
    )

    type = models.CharField(
        verbose_name=_("Type"),
        max_length=30,
        db_index=True
    )

    is_sliding_calendar = models.BooleanField(
        default=True
    )

    display_tasks = models.BooleanField(
        default=True
    )

    display_projects = models.BooleanField(
        default=False
    )

    display_all_tasks = models.BooleanField(
        default=False
    )

    # This field is intended to be used by the NotificationFeed only.
    # It's used to detect periodically when an item enter or exit the SavedFilter.
    # It should NOT be relied upon to get the current items in the SavedFilter.
    # Not also that the field will be kept up to date only while there's a
    # NotificationFeed linked to this SavedFilter
    notification_feed_instance_ids = pg_fields.ArrayField(
        base_field=models.PositiveIntegerField(),
        default=list,
        verbose_name=_("Champ technique pour le NotificationFeed"),
    )

    class Meta:
        verbose_name = _('Item Saved Filter')
        verbose_name_plural = _('Items Saved Filters')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def refresh_notification_feed_instance_ids(self):
        from pilot.notifications.feed import get_items_ids_in_saved_filter
        self.notification_feed_instance_ids = get_items_ids_in_saved_filter(self)

    def save(self, *args, **kwargs):
        # Each time we save, we may update the filter field.
        # Keep the notification_feed_instance_ids up to date
        # so we don't trigger an avalanche of notifications.
        # We could do this in a Job for performance,
        # but this could open a small timeframe where
        # the notification avalanche could be triggered by an Item update.
        self.refresh_notification_feed_instance_ids()
        super(SavedFilter, self).save(*args, **kwargs)

    @property
    def is_calendar(self):
        return self.type == self.TYPE_CALENDAR

    @property
    def is_list(self):
        return self.type == self.TYPE_LIST

    def get_absolute_url(self):
        if self.is_list:
            return reverse('ui_saved_filter_list', kwargs={'saved_filter_pk': self.pk})
        elif self.is_calendar:
            return reverse('ui_saved_filter_calendar', kwargs={'saved_filter_pk': self.pk})


class SharedFilterManager(models.Manager):
    def get_queryset(self):
        """Always fetch the related SavedFilter object."""
        return super(SharedFilterManager, self).get_queryset().select_related('saved_filter')


class InternalSharedFilter(CreateTrackingModel, models.Model):
    """
    A filter shared with users of the desk.
    """

    saved_filter = models.ForeignKey(
        SavedFilter,
        on_delete=models.CASCADE,
        verbose_name=_("Saved filter"),
        related_name='internal_shared_filters'
    )

    users = models.ManyToManyField(
        PilotUser,
        verbose_name=_("Destinataires"),
        related_name='internal_shared_filters',
    )

    message = pg_fields.JSONField(
        verbose_name=_("Message"),
        default=dict,
        blank=True
    )

    class Meta:
        verbose_name = _('Internal Shared Filter')
        verbose_name_plural = _('Internal Shared Filters')
        ordering = ['-created_at']

    objects = SharedFilterManager()

    def get_absolute_url(self):
        return self.saved_filter.get_absolute_url()


class PublicSharedFilter(CreateTrackingModel, models.Model):
    """
    A shared custom filter for items.
    When an SavedFilter is created, it can be shared with anonymous users via PublicSharedFilter.
    """

    saved_filter = models.ForeignKey(
        SavedFilter,
        on_delete=models.CASCADE,
        verbose_name=_("Saved filter"),
        related_name='public_shared_filters'
    )

    email = models.EmailField(
        verbose_name=_("Email"),
        max_length=254,
        help_text=_("Envoyer à cette adresse (une seule)")
    )

    password = models.CharField(
        verbose_name=_("Mot de passe"),
        max_length=254,
        blank=True,
        help_text=_("Un mot de passe (optionnel) pour protéger le calendrier "
                    "(sera indiqué dans l'email avec l'url de partage")
    )

    token = models.CharField(
        verbose_name=_("Token"),
        max_length=32
    )

    items_locked = models.BooleanField(
        verbose_name="Contenus verrouillés",
        default=False,
        help_text=_('Les contenus dans le calendrier ne seront pas cliquables si cette case est cochée')
    )

    class Meta:
        verbose_name = _('Public Shared Filter')
        verbose_name_plural = _('Public Shared Filters')
        ordering = ['-created_at']

    objects = SharedFilterManager()

    def __str__(self):
        return _("{0} partagé avec {1}").format(self.saved_filter.title, self.email)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = generate_token()
        # Ensure that `saved_filter` and `token` fields are unique together.
        while PublicSharedFilter.objects.filter(token=self.token).exclude(pk=self.pk).exists():
            self.token = generate_token()
        super(PublicSharedFilter, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns the public URL for this shared custom filter."""
        return reverse(
            'ui_shared_filter',
            kwargs={'token': self.token,}
        )

    @property
    def password_required_url(self):
        return reverse(
            'ui_shared_filter_password_required',
            kwargs={'token': self.token, }
        )
