import datetime
import json

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.core import exceptions
from django.core import serializers as django_serializers
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from pilot.utils.forms.fields import NaiveDateTimeField as FormNaiveDateTimeField


class NonErasingGenericForeignKey(GenericForeignKey):
    """
    The default implementation of GenericForeignKey will force the content_type and foreign_key values to None
    if the linked object cannot be resolved ( because it has been deleted ).

    This implementation override this behaviour to instead retain those values.
    """
    def __set__(self, instance, value):
        if value is not None:
            ct = self.get_content_type(obj=value)
            fk = value.pk

            setattr(instance, self.ct_field, ct)
            setattr(instance, self.fk_field, fk)
            self.set_cached_value(instance, value)


class NaiveDateTimeField(models.DateTimeField):
    """
    A field that will only work with naive datetime.

    Internally, it stores the datetimes in UTC,
    but the value in input/output are always naive.
    """
    default_error_messages = {
        'aware_datetime': _("'%(value)s' value is an aware-datetime, but"
                            "NaiveDateTimeField accepts only naive-datetimes"),
    }
    description = _("Date (with naive time)")

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value

        # Convert aware datetime on UTC to naive datetime
        return timezone.make_naive(value, timezone.utc)

    def to_python(self, value):
        # Return None, date and datetime as-is.
        if value is None:
            return value
        if isinstance(value, (datetime.datetime, datetime.date)):
            return value

        # Try to parse strings
        return super(NaiveDateTimeField, self).to_python(value)

    def get_prep_value(self, value):
        value = super(models.DateTimeField, self).get_prep_value(value)
        value = self.to_python(value)

        if value is not None and timezone.is_aware(value):
            raise exceptions.ValidationError(
                self.error_messages['aware_datetime'],
                code='aware_datetime',
                params={'value': value},
            )

        # Convert naive datetime to aware datetime on UTC
        if value:
            value = timezone.make_aware(value, timezone.utc)

        return value

    # Form field used only in the django admin  (Task deadline for example)
    def formfield(self, **kwargs):
        defaults = {'form_class': FormNaiveDateTimeField}
        defaults.update(kwargs)
        return super(NaiveDateTimeField, self).formfield(**defaults)


class UpdateTrackingModel(models.Model):
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Mis à jour par"),
        related_name='%(class)s_updated',
        null=True,
        blank=True,
    )
    # !!! BEWARE !!!
    # Do not use "auto_now" on this field, because it would be erased during data migrations !
    updated_at = models.DateTimeField(
        verbose_name=_("Mis à jour à"),
        blank=True,
        db_index=True
    )

    class Meta:
        abstract = True

    # Set to True on an instance if you want to prevent the automatic update of the field `updated_at`
    prevent_updated_at = False

    def save(self, *args, **kwargs):
        if not self.prevent_updated_at:
            self.updated_at = timezone.now()
        return super(UpdateTrackingModel, self).save(*args, **kwargs)


class CreateTrackingModel(models.Model):
    created_at = models.DateTimeField(
        verbose_name=_("Créé le"),
        default=timezone.now,
        db_index=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Créé par"),
        related_name='%(class)s_created'
    )

    class Meta:
        abstract = True


class ChangeTrackingModel(CreateTrackingModel, UpdateTrackingModel):
    class Meta:
        abstract = True


class OptionalCreatorChangeTrackingModel(UpdateTrackingModel):
    created_at = models.DateTimeField(
        verbose_name=_("Créé le"),
        default=timezone.now,
        db_index=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Créé par"),
        related_name='%(class)s_created',
        null=True,
        blank=True
    )

    class Meta:
        abstract = True


class HideableModel(models.Model):
    hidden = models.BooleanField(
        verbose_name=_("Invisible"),
        default=False,
        db_index=True
    )

    class Meta:
        abstract = True

    def hide(self, user):
        """
        We don't actually destroy the instance, but set its "hidden" flag to True
        """
        self.hidden = True
        self.updated_by = user
        self.save()


def get_fields_to_serialize(model, exclude=[]):
    """
    This code is directly copied from reversion,
    but use exclude as an exclusion list
    """
    opts = model._meta.concrete_model._meta
    fields = (field.name for field in opts.local_fields + opts.local_many_to_many)
    fields = (opts.get_field(field) for field in fields if field not in exclude)
    for field in fields:
        if field.remote_field:
            yield field.name
        else:
            yield field.attname


def serialize_model_instance(instance, exclude=[]):
    """
    Make a json representation of a model's instance.
    Field names in the exclude list are not serialized.

    This feature is inspired by the reversion lib, and the output from the two are compatible.
    """
    serialization_format = 'json'
    # Django serializer always return a string
    # And always process list of objects
    serialized_string = django_serializers.serialize(
        serialization_format,
        (instance,),
        fields=list(get_fields_to_serialize(instance, exclude)),
    )

    # We want to store the json for our single instance, so :
    # 1/ Load the json string
    # 2/ Take the first and only element : our instance
    return json.loads(serialized_string)[0]


def deserialize_model_instance(serialized_data):
    serialization_format = 'json'
    return list(django_serializers.deserialize(
        serialization_format,
        json.dumps([serialized_data]),
    ))[0]
