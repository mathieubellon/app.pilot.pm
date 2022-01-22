from django.db import models, transaction
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres import fields as pg_fields

from pilot.desks.models import Desk
from pilot.utils.models import ChangeTrackingModel, HideableModel, serialize_model_instance, CreateTrackingModel, \
    deserialize_model_instance


class ItemTypeManager(models.Manager):
    def get_queryset(self):
        """Only visible ItemType."""
        return super(ItemTypeManager, self).get_queryset().filter(hidden=False)


class ItemType(ChangeTrackingModel,
               HideableModel,
               models.Model):
    """
    User defined item types.
    """

    NON_SERIALIZED_FIELDS = (
        'updated_at',  # No need to store that, there's already a created_at on EditSession
    )

    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='item_types'
    )

    name = models.CharField(
        verbose_name=_("Nom"),
        max_length=500
    )

    description = models.CharField(
        verbose_name=_("Description"),
        max_length=500,
        blank=True
    )

    content_schema = pg_fields.JSONField(
        verbose_name=_("Schema"),
        default=list,
        blank=True
    )

    metadata_schema = pg_fields.JSONField(
        verbose_name=_("Schema des metadata"),
        default=list,
        blank=True
    )

    task_group = models.ForeignKey(
        'tasks.TaskGroup',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    icon_name = models.CharField(
        verbose_name=_("Nom d'icône"),
        max_length=100,
        blank=True
    )

    objects = ItemTypeManager()
    all_the_objects = models.Manager()  # for django admin

    class Meta:
        verbose_name = _("Type de contenu")
        verbose_name_plural = _("Types de contenu")
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if self.hidden:
            return None
        return reverse('ui_item_types_edit', kwargs={'item_type_pk': self.pk})

    def save(self, *args, **kwargs):
        # Save the ItemType and its snapshot into a transaction to stay consistent
        with transaction.atomic():
            # Save the item type normally
            super(ItemType, self).save(**kwargs)
            self.take_snapshot()

    def take_snapshot(self):
        serialized_data = serialize_model_instance(self, self.NON_SERIALIZED_FIELDS)
        # The creator of the snapshot is the last updater of the item
        # If we create the first snapshot, there won't be any item updater, so use the creator
        creator = self.updated_by or self.created_by
        # Save the snapshot
        return ItemTypeSnapshot.objects.create(
            item_type=self,
            created_by=creator,
            serialized_data=serialized_data
        )

    @property
    def last_snapshot(self):
        """
        Returns the most recent snapshot, which should mirror exactly the current state
        """
        try:
            return self.snapshots.latest()
        except ItemTypeSnapshot.DoesNotExist:
            # Some old ItemType had no ItemTypeSnapshot created, we should create them in this case
            return self.take_snapshot()


class ItemTypeSnapshot(CreateTrackingModel):

    item_type = models.ForeignKey(
        ItemType,
        on_delete=models.SET_NULL,
        verbose_name=_("Type de contenu"),
        related_name='snapshots',
        null=True
    )

    # Freeze the data of the ItemType at the time of the snapshot
    # Do not allow null, as there should always be some data to serialize
    serialized_data = pg_fields.JSONField(
        verbose_name=_("ItemType serialized data"),
        default=dict
    )

    class Meta:
        verbose_name = _("Snapshot type de contenu")
        verbose_name_plural = _("Snapshots types de contenu")
        ordering = ('-created_at',)
        get_latest_by = 'created_at'

    def as_item_type(self):
        return deserialize_model_instance(self.serialized_data)

    @property
    def content_schema(self):
        return self.serialized_data.get('fields', {}).get('content_schema', [])
