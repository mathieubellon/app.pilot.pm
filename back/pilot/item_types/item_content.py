import copy
import logging
from collections import OrderedDict
import datetime

from django.contrib.postgres import fields as pg_fields
from django.db import models
from django.template.defaultfilters import filesizeformat
from django.utils.html import mark_safe
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from pilot.item_types.item_content_fields import create_content_field, validate_field_schema, \
    get_content_schema_for_frontend, sanitize_content_schema, HELP_TEXT, ASSET_TYPE, get_elastic_field_size, \
    get_elastic_field_name, AUTO_COMPLETE_TYPE
from pilot.utils.prosemirror.prosemirror import EMPTY_PROSEMIRROR_DOC
from pilot.utils.serialization import SerializationFormat, get_dialect

logger = logging.getLogger(__name__)

DATE_FORMAT = '%d/%m/%Y'

class ItemContentMixin(models.Model):
    """
    A mixin to add dynamic content storage to a model, through a jsonb field.

    Used as a base for Item and EditSession.

    Convention : when using a variable that may hold any subclass of ItemContentMixin, name it "item_content".
    The actual content is accessible with item_content.content.
    Of course, if you know the concrete type, use it directly : "item", "session", etc...
    """
    json_content = pg_fields.JSONField(
        verbose_name=_("Content data"),
        default=dict,
        blank=True
    )

    class Meta:
        abstract = True

    def get_content_schema_impl(self):
        """
        Should be re-implemented by subclasses.

        Returns the content schema to use to serialize/deserialize the json content
        """
        return []

    def get_content_schema(self):
        """
        Returns the content schema to use to serialize/deserialize the json content.

        Will default to an empty list if no schema is provided.
        """
        return self.get_content_schema_impl() or []

    _field_schema_map = None
    _converters = None

    def _init_field_schema_map(self):
        if self._field_schema_map is None:
            # Preserve the order of the fields in the "schema" declaration
            self._field_schema_map = OrderedDict()
            for field_schema in self.generate_all_field_schema(self.json_content):
                self._field_schema_map[field_schema['name']] = field_schema

    def generate_all_field_schema(self, content):
        """
        Generate all field schemas, taking into account the elastic fields, expanding them as needed.
        """
        for field_schema in self.get_content_schema():
            if field_schema.get('elastic'):
                for i in range(get_elastic_field_size(field_schema, content)):
                    elastic_schema = copy.deepcopy(field_schema)
                    elastic_schema['name'] = get_elastic_field_name(field_schema['name'], i)
                    elastic_schema['label'] = '{} ({})'.format(field_schema['label'], i+1)
                    yield elastic_schema
            else:
                yield field_schema

    def get_all_field_schema(self):
        """
        Get a list of all field schema, taking into account the elastic fields
        """
        self._init_field_schema_map()
        return self._field_schema_map.values()

    def get_field_schema(self, field_name):
        """
        Get a field schema by name, taking into account the elastic fields
        """
        self._init_field_schema_map()
        return self._field_schema_map.get(field_name)

    def get_content_field(self, field_name):
        """
        Get a content field by name, taking into account the elastic fields
        """
        field_schema = self.get_field_schema(field_name)
        if not field_schema:
            return None
        return create_content_field(field_schema)

    @property
    def content(self):
        """
        Alias for self.json_content
        """
        return self.json_content

    @content.setter
    def content(self, content):
        """
        Alias for self.json_content
        """
        self.json_content = content

    def clean_content(self):
        # Ensure we have a fresh field schema map, in case of a change in the elastic fields
        self._field_schema_map = None

        for field_name, value in self.json_content.items():
            # DRF3 does not handle anymore None into field.to_internal_value().
            # If value is None, just return None, or we'll get an exception.
            # See rest_framework/serializers.py:491
            if value is None:
                continue

            content_field = self.get_content_field(field_name)
            serializer = content_field.create_serializer_field()

            # We try to validate the value and serialize it
            try:
                value = serializer.run_validation(value)
            # However, its now possible to save invalid data, so the deserialization may fail.
            # In this case, use the invalid value as-is, so the user will see an error message
            # along with the invalid value.
            except ValidationError:
                # When choice content are not valid anymore, fallback to None
                if isinstance(serializer, serializers.ChoiceField):
                    value = None

            self.json_content[field_name] = value

    def _init_converters(self):
        # The cache is already populated, nothing to do
        if self._converters is not None:
            return

        # Preserve the order of the fields in the "schema" declaration
        self._converters = OrderedDict()

        for field_schema in self.get_all_field_schema():
            field_name = field_schema['name']
            self._converters[field_name] = ItemContentValueConverter(
                value=self.json_content.get(field_name),
                field_schema=field_schema
            )

    def serialize(self, format=None):
        """
        Content serialized for Public API, represented as a dict field_name => serialized_value
        """
        return {
            name: converter.serialize(format)
            for name, converter in self.converters.items()
        }

    @property
    def converters(self):
        """
        The content represented as a dict key => ItemContentValueConverter
        """
        self._init_converters()
        return self._converters

    @property
    def title(self):
        # Item managers will defer the `json_content` field, but will query a special _title field.
        # Take this when available. Else, take it inside the `json_content` field.
        if hasattr(self, '_title'):
            title = self._title
        else:
            title = self.json_content.get('title', '')

        return str(title or '')


class ItemContentValueConverter(object):
    """
    Wrap a simple value with formatting methods.

    This is useful to convert the raw value to one of the supported output :
     - html
     - plain text
     - public API
    """

    def __init__(self, value, field_schema):
        self.value = value
        self.field_schema = field_schema
        self.type = field_schema['type']
        self.name = field_schema['name']
        self.label = field_schema.get('label', 'name')
        if isinstance(self.label, dict):
            self.label = self.label['fr']
        self.choices = field_schema.get('choices')
        self.content_field = create_content_field(field_schema)
        self.is_prosemirror = self.content_field.is_prosemirror
        self.is_asset = self.content_field.type == ASSET_TYPE

        # Optimize multiple calls by caching conversion result.
        # Currently, this is only used in the desk export feature
        self._serialization_cache = {}

    def __str__(self):
        value = self.value

        if isinstance(value, datetime.date):
            value = value.strftime(DATE_FORMAT)

        return str(value)

    def __repr__(self):
        return "<ItemContentValueConverter : label={} value={}>".format(self.label, self.value).encode()

    def __eq__(self, other_value):
        if isinstance(other_value, ItemContentValueConverter):
            other_value = other_value.value
        return self.value == other_value

    def _do_conversion(self, dialect):
        if self.content_field.type == HELP_TEXT:
            return self.field_schema.get('help_text', '')

        value = self.value

        if value in [None, '']:
            return ''

        elif isinstance(value, datetime.date):
            value = value.strftime(DATE_FORMAT)

        elif self.choices and not self.type == AUTO_COMPLETE_TYPE:
            choices_dict = dict(self.choices)
            if isinstance(self.value, (list, tuple)):
                # Multiple choices
                labels = [choices_dict[val] for val in self.value]
                value = dialect.newline.join(' - {}'.format(val) for val in labels)
            else:
                # Single choice
                value = choices_dict.get(self.value, '')

        elif self.is_prosemirror:
            value = dialect.pm_converter(self.value)

        elif self.is_asset:
            size = filesizeformat(self.value.get('size'))
            link = dialect.link_serializer(
                self.value.get('file_url'),
                self.value.get('name')
            )
            value = _("Télécharger (%(size)s) : %(link)s") % {
                'size': size,
                'link': link
            }

        return mark_safe(value)

    def serialize(self, format=None):
        """
        Serialize in the given format
        """
        if not format or format == SerializationFormat.RAW:
            return self.value

        if format not in self._serialization_cache:
            dialect = get_dialect(format)
            self._serialization_cache[format] = self._do_conversion(dialect)

        return self._serialization_cache[format]

    # This is required for ItemContentExporter.export_to_html and ItemContentExporter.export_to_pdf
    # which use a django template in exporthtml.html and exportpdf.html
    @property
    def as_html(self):
        return self.serialize(SerializationFormat.HTML)


# Setup initial data into the v1.0 content
def init_item_content(content, content_schema, creation=False):
    for field_schema in content_schema:
        # Do not override values that are already set in the content dict.
        # This may happens during item copy
        if field_schema['name'] in content:
            continue

        content_field = create_content_field(field_schema)

        # Fields shown in creation/public should be initialized by the user,
        # do not override them
        if creation and field_schema.get('show_in_creation'):
            continue

        initial = None
        if content_field.is_prosemirror:
            # Special case for prosemirror documents that should always get initialized to an EMPTY_DOC
            initial = EMPTY_PROSEMIRROR_DOC
        initial = field_schema.get('initial', initial)
        content[field_schema['name']] = initial

# ===== Serializer Field for Content Schema =====


def validate_content_schema(content_schema):
    existing_names = [field_schema.get('name') for field_schema in content_schema]

    for field_schema in content_schema:
        validate_field_schema(field_schema)

        # Generate names for new fields
        label = field_schema.get('label', '')

        # Generate names for new fields
        if not field_schema.get('name'):
            name = slugify(label)
            i = 1
            # Ensure uniqueness of names
            while name in existing_names:
                name = "{}-{}".format(slugify(label), i)
                i += 1

            field_schema['name'] = name
            existing_names.append(name)


class ContentSchemaField(serializers.JSONField):
    """
    A serializer field to serialize a content schema.

    In input, this will validate the schema, and sanitize it against malicious html.
    In output, this will adapt the schema for the frontend.
    """
    default_validators = [
        validate_content_schema
    ]

    def to_representation(self, content_schema):
        return get_content_schema_for_frontend(content_schema)

    def to_internal_value(self, content_schema):
        return sanitize_content_schema(content_schema)
