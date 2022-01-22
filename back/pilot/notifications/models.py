from collections import namedtuple

import arrow
from datetime import timedelta

from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres import fields as pg_fields

from pilot.activity_stream.models import Activity
from pilot.assets.models import AssetRight
from pilot.desks.models import Desk
from pilot.itemsfilters.models import SavedFilter
from pilot.notifications.const import NotificationType
from pilot.pilot_users.models import PilotUser
from pilot.tasks.models import Task
from pilot.utils.models import NonErasingGenericForeignKey
from pilot.utils.token_generator import generate_token


class UnreadNotificationManager(models.Manager):
    def get_queryset(self):
        """Only unread notifications."""
        return super(UnreadNotificationManager, self).get_queryset().filter(is_read=False)


class ReadNotificationManager(models.Manager):
    def get_queryset(self):
        """Only read notifications."""
        return super(ReadNotificationManager, self).get_queryset().filter(is_read=True)


class Notification(models.Model):
    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='notifications',
        null=True
    )

    type = models.CharField(
        verbose_name=_("Type de notification"),
        choices=NotificationType.CHOICES,
        max_length=100,
        db_index=True,
    )

    send_by = models.ForeignKey(
        PilotUser,
        on_delete=models.CASCADE,
        verbose_name=_("Notification envoyée par"),
        related_name='notifications_send'
    )

    to = models.ForeignKey(
        PilotUser,
        on_delete=models.CASCADE,
        verbose_name=_("Notification envoyée à"),
        related_name='notifications_received'
    )

    content = models.TextField(
        verbose_name=_("Contenu de la notification"),
        blank=True
    )

    linked_object_id = models.IntegerField(
        verbose_name=_("Object concerné"),
        null=True
    )

    linked_object_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='notification',
        verbose_name=_("Content type de l'objet concerné"),
        max_length=100,
        null=True
    )

    linked_object = NonErasingGenericForeignKey('linked_object_content_type', 'linked_object_id')

    target_url = models.CharField(
        verbose_name=_("URL cible"),
        max_length=300,
        blank=True
    )

    send_at = models.DateTimeField(
        verbose_name=_("Notification envoyée à"),
        default=timezone.now
    )

    is_read = models.BooleanField(
        verbose_name=_("Notification lue ?"),
        default=False
    )

    source_feed = models.ForeignKey(
        'NotificationFeed',
        on_delete=models.SET_NULL,
        verbose_name=_("Notification envoyée par un flux"),
        related_name='notifications',
        null=True
    )

    # Additionnal arbitrary data the notification creator wish to store in the db
    data = pg_fields.JSONField(
        verbose_name=_("Data"),
        default=dict
    )

    token = models.CharField(
        verbose_name=_("Token"),
        max_length=32
    )

    objects = models.Manager()
    unread_objects = UnreadNotificationManager()
    read_objects = ReadNotificationManager()

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = generate_token()

        # Ensure that token fields are unique together.
        while Notification.objects. \
                filter(token=self.token). \
                exclude(pk=self.pk). \
                exists():
            self.token = generate_token()

        super(Notification, self).save(*args, **kwargs)

    def get_absolute_url(self):
        # If we cannot redirect to the target, then this notification should not have a goto url
        if not self.get_target_url():
            return None

        return reverse('notifications_goto', kwargs={'token': self.token})

    def get_target_url(self):
        if self.target_url:
            return self.target_url

        target_object = self.linked_object
        if target_object is None or not hasattr(target_object, 'get_absolute_url'):
            return None

        url = target_object.get_absolute_url()
        # url may be None if the object is hidden
        if not url:
            return None

        if self.annotation_uuid:
            url += f'?scrollto=annotation-{self.annotation_uuid}'
        elif self.comment_id:
            url += f'?scrollto=comment-{self.comment_id}'
        return url

    @property
    def comment_id(self):
        return self.data.get('comment', {}).get('id')

    @property
    def annotation_uuid(self):
        return self.data.get('annotation_uuid')


class NotificationFeed(models.Model):
    FEED_TYPE_ACTIVITY_STREAM = 'activity_stream'
    FEED_TYPE_ITEM_SAVED_FILTER = 'item_saved_filter'

    FEED_TYPE_CHOICES = (
        (FEED_TYPE_ACTIVITY_STREAM, _("Activity Stream")),
        (FEED_TYPE_ITEM_SAVED_FILTER, _("Item Saved Filter")),
    )

    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='notification_feeds'
    )

    user = models.ForeignKey(
        PilotUser,
        on_delete=models.CASCADE,
        verbose_name=_("Abonné"),
        related_name='notification_feeds'
    )

    feed_type = models.CharField(
        max_length=50,
        choices=FEED_TYPE_CHOICES,
        verbose_name=_("Type de flux")
    )

    send_email = models.BooleanField(
        verbose_name=_("Envoyer un email ?"),
        default=True
    )

    display_in_app = models.BooleanField(
        verbose_name=_("Afficher la notification in-app ?"),
        default=True
    )

    # ===================
    # Activity Stream Feed
    # ===================

    # The verb that are watched.
    # Empty list means "All verbs"
    activity_verbs = pg_fields.ArrayField(
        base_field=models.CharField(
            choices=Activity.ACTIVE_VERB_CHOICES,
            max_length=100
        ),
        default=list,
        blank=True
    )

    # The target content type that is watched
    activity_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    # The target object id that is watched
    activity_object_id = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    # The actor that is watched
    activity_actor = models.ForeignKey(
        PilotUser,
        on_delete=models.CASCADE,
        related_name='notification_feeds_actor',
        blank=True,
        null=True
    )

    # ===================
    # Item Saved Filter Feed
    # ===================

    # The item saved filter that is watched
    saved_filter = models.ForeignKey(
        SavedFilter,
        on_delete=models.CASCADE,
        verbose_name=_("Saved filter"),
        related_name='notification_feeds',
        null=True
    )

    class Meta:
        unique_together = ('user', 'saved_filter')

    def save(self, *args, **kwargs):
        # Init the notification_feed_instance_ids when we create the NotificationFeed
        self.saved_filter.refresh_notification_feed_instance_ids()
        self.saved_filter.save()
        super(NotificationFeed, self).save(*args, **kwargs)


ReminderDeltaUnit = namedtuple('ReminderDeltaUnit', ['name', 'verbose_name', 'seconds'])


class Reminder(models.Model):
    TARGET_TYPE_TASK_DEADLINE = 'task_deadline'
    TARGET_TYPE_ASSET_RIGHT_EXPIRY = 'asset_right_expiry'
    TARGET_TYPE_CHOICES = (
        (TARGET_TYPE_TASK_DEADLINE, _("Task deadline")),
        (TARGET_TYPE_ASSET_RIGHT_EXPIRY, _("Asset right expiry")),
    )

    DELTA_UNITS_CHOICES = (
        ('hours', _("Heures")),
        ('days', _("Jours")),
        ('weeks', _("Semaines")),
    )

    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='reminders'
    )

    user = models.ForeignKey(
        PilotUser,
        on_delete=models.CASCADE,
        related_name='reminders'
    )

    # ===================
    # Notification
    # ===================

    is_notification_sent = models.BooleanField(
        verbose_name=_("Notification envoyée ?"),
        default=False
    )

    notification = models.OneToOneField(
        Notification,
        on_delete=models.SET_NULL,
        verbose_name=_("Objet notification créé"),
        related_name='reminder',
        null=True
    )

    cancelled = models.BooleanField(
        verbose_name=_("Rappel annulé ?"),
        default=False
    )

    # ===================
    # Target
    # ===================

    target_type = models.CharField(
        max_length=50,
        choices=TARGET_TYPE_CHOICES,
        verbose_name=_("Type de rappel")
    )

    target_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        verbose_name=_("Target task"),
        related_name='reminders',
        null=True
    )

    target_asset_right = models.ForeignKey(
        AssetRight,
        on_delete=models.CASCADE,
        verbose_name=_("Target asset right"),
        related_name='reminders',
        null=True
    )

    # ===================
    # Time delta and ripe date time
    # ===================

    delta_unit = models.CharField(
        max_length=10,
        choices=DELTA_UNITS_CHOICES,
        verbose_name=_("Unité du délai")
    )

    delta_value = models.PositiveIntegerField(
        verbose_name=_("Valeur du délai")
    )

    ripe_date_time = models.DateTimeField(
        verbose_name=_("Date-heure de déclenchement de la notification de rappel"),
    )

    class Meta:
        # Ensure a stable ordering on the UX
        ordering = ['id']

    def save(self, *args, **kwargs):
        # Tallying will either save or delete the reminder
        self.tally()

    def set_target_for_creation(self, target_id):
        if self.target_type == self.TARGET_TYPE_TASK_DEADLINE:
            self.target_task = Task.objects.get(id=target_id)
        elif self.target_type == self.TARGET_TYPE_ASSET_RIGHT_EXPIRY:
            self.target_asset_right = AssetRight.objects.get(id=target_id)
        else:
            raise ValueError(f"Incorrect target type {self.target_type}")

    def get_target(self):
        if self.target_type == self.TARGET_TYPE_TASK_DEADLINE:
            return self.target_task
        elif self.target_type == self.TARGET_TYPE_ASSET_RIGHT_EXPIRY:
            return self.target_asset_right
        else:
            return None

    def get_delta(self):
        # Compute a timedelta, from the delta unit and the delta value
        return timedelta(**{self.delta_unit: self.delta_value})

    def is_ripe(self):
        return self.ripe_date_time < arrow.now(self.user.timezone)

    def get_target_date_time(self):
        if self.target_type == self.TARGET_TYPE_TASK_DEADLINE:
            deadline = self.target_task.deadline
            if not deadline:
                return None

            # The task deadline is stored as a naive datetime.
            # We need to interpret it relative to the user timezone,
            # so the user has a reminder relative to its local time, and not relative to UTC.
            return arrow.get(deadline, self.user.timezone).datetime

        elif self.target_type == self.TARGET_TYPE_ASSET_RIGHT_EXPIRY:
            # The asset expiry is a date without time.
            # Interpret it as midnight, relative to the user timezone.
            return arrow.get(self.target_asset_right.expiry, self.user.timezone).datetime

    def tally(self):
        """
        We need to tally the reminder when :
        1/ We create a new reminder
        2/ We update an existing reminder
        3/ We update the datetime on the target of a reminder

        If the datetime has been deleted on the target, the reminder is deleted.
        Else, we recompute a new ripe datetime for the reminder.
        If this new ripe datetime is already in the past, then we cancel the reminder.
        If a notification had already been sent for the reminder, but its not ripe anymore,
        then we remove the link with the notification to reschedule a new notification
        """
        target_date_time = self.get_target_date_time()

        if target_date_time is None:
            self.delete()
            return

        # Compute a new ripe datetime
        self.ripe_date_time = target_date_time - self.get_delta()
        # Cancel the reminder if it's already ripe when tallying.
        # May un-cancel a reminder that was cancelled but is now scheduled, which is intended
        self.cancelled = self.is_ripe() and not self.is_notification_sent
        # Remove the already-sent notification if the reminder is not ripe anymore,
        # so a new notification will be sent when the reminder will be ripe
        if self.is_notification_sent and not self.is_ripe():
            self.is_notification_sent = False
            self.notification = None

        super(Reminder, self).save()
