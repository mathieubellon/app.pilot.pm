import datetime

from django.core.exceptions import FieldError
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from rest_framework import serializers, ISO_8601
from rest_framework.relations import ManyRelatedField

from pilot.pilot_users.models import PilotUser
from pilot.utils.html import sanitize_user_input_html


class DocumentedSerializerMixin(serializers.Serializer):
    """
    A Mixin to declare the help_texts of serializer fields in a single "doc" attribute,
    instead of cluttering each field declaration.
    """
    def get_fields(self):
        fields = super(DocumentedSerializerMixin, self).get_fields()

        doc = getattr(self, 'doc', {})
        for field_name, help_text in doc.items():
            if field_name in fields:
                fields[field_name].help_text = help_text

        return fields


class NaiveDateTimeField(serializers.DateTimeField):
    """
    A serializer field that handle only naive datetimes.

    Will fail on any aware datetime.
    """
    NOT_NAIVE_ERROR = "'{}' value is an aware-datetime, but NaiveDateTimeField accepts only naive-datetimes"

    def ensure_naive(self, value):
        if timezone.is_aware(value):
            raise ValueError(self.NOT_NAIVE_ERROR.format(value))
        return value

    def to_internal_value(self, value):
        # Handle None and empty strings
        if not value:
            return None

        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            self.fail('date')

        if isinstance(value, datetime.datetime):
            return self.ensure_naive(value)

        try:
            parsed = parse_datetime(value)
        except (ValueError, TypeError):
            pass
        else:
            if parsed is not None:
                return self.ensure_naive(parsed)

        self.fail('invalid', format=ISO_8601)

    def to_representation(self, value):
        if not value:
            return None

        self.ensure_naive(value)

        return value.isoformat()


class Iso8601Field(serializers.DateTimeField):
    """
    A field that ensure the value is a datetime encoded in ISO 8601
    but does not convert it to a python datetime object.

    This is useful for validating a date that will be stored in json
    (such as in a json field)
    """
    format = ISO_8601

    def to_internal_value(self, value):
        try:
            parsed = parse_datetime(value)
        except (ValueError, TypeError):
            parsed = None

        if parsed:
            return value
        else:
            self.fail('invalid', format=ISO_8601)

    def to_representation(self, value):
        try:
            parse_datetime(value)
        except (ValueError, TypeError):
            self.fail('invalid', format=ISO_8601)
        else:
            return value


class EmailLowerCaseField(serializers.EmailField):
    """
    A serializer field which ensures that all emails are in lower case.

    Django does not automatically lower the case in email addresses because as stated in RFC 2821:
    "The local-part of a mailbox MUST BE treated as case sensitive."

    See:
    https://code.djangoproject.com/ticket/5605
    https://code.djangoproject.com/ticket/17561

    But PILOT-154 was discussed and we decided to lower the case.
    """
    def to_internal_value(self, value):
        return super(EmailLowerCaseField, self).to_internal_value(value).lower()


class SmartPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """
    A PrimaryKeyRelatedField that make an auto-discovery of the related model if not provided.

    Will also restrict the queryset to the current desk.
    Will also restrict the queryset to the permitted related instances, if the user is a restricted editor.
    """

    def __init__(self, **kwargs):
        self.restrict_desk = kwargs.pop('restrict_desk', True)
        self.restrict_permissions = kwargs.pop('restrict_permissions', True)
        self.use_id_for_internal_value = kwargs.pop('use_id_for_internal_value', True)
        super(SmartPrimaryKeyRelatedField, self).__init__(**kwargs)

    def get_queryset(self):
        if isinstance(self.parent, ManyRelatedField):
            # This happen when many=True is used
            source = self.parent.source
        else:
            source = self.source

        model = self.root.Meta.model
        queryset = self.queryset
        if not queryset:
            queryset = model._meta.get_field(source).related_model.objects.all()

        request = self.context['request']

        desk = request.desk
        if desk and self.restrict_desk:
            # Special-case for users, because we also want to include deactivated users
            if queryset.model == PilotUser:
                queryset = queryset.filter(Q(desks=desk) | Q(desks_deactivated=desk) | Q(wiped=True))

            else:
                try:
                    queryset = queryset.filter(desk=desk)
                except FieldError:
                    try:
                        queryset = queryset.filter(desks=desk)
                    except FieldError:
                        raise Exception('SmartPrimaryKeyRelatedField must be used on a model which have a desk field')

        user = request.user
        if user and self.restrict_permissions and hasattr(queryset, 'filter_by_permissions'):
            queryset = queryset.filter_by_permissions(user)

        return queryset

    def to_internal_value(self, data):
        # Ensure the related object exists, then use its pk
        related = super(SmartPrimaryKeyRelatedField, self).to_internal_value(data)
        if self.use_id_for_internal_value:
            return related.pk
        else:
            return related


class SanitizedHtmlField(serializers.CharField):
    """
    A serializer field to accept user-submitted html code that must be sanitized against malicious injection.
    """
    def to_internal_value(self, value):
        return sanitize_user_input_html(value)
