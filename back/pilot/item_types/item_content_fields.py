import copy
import logging

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from pilot.assets.models import Asset
from pilot.utils.html import sanitize_user_input_html

logger = logging.getLogger(__name__)


class ContentField(object):
    type = None
    label = None
    description = None
    serializer_class = serializers.Field
    is_prosemirror = False  # True if the field use a prosemirror editor
    # Usable attributes :
    can_be_required = True
    can_be_elastic = False
    with_initial = False
    with_placeholder = False
    with_max_length = False
    with_validate_max_length = False
    with_min_value = False
    with_max_value = False
    with_choices = False
    with_regex = False

    def __init__(self, schema):
        self.schema = schema
        self.name = schema.get('name', None)

    def get_extra_serializer_kwargs(self):
        """
        Hook for subclasses : Field-specific keywords arguments for the serializer
        """
        return {}

    def get_serializer_kwargs(self):
        """
        Return keyword arguments for the serializer
        """
        required = self.can_be_required and self.schema.get('required')
        serializer_kwargs = {
            'required': required,
            'allow_null': not required,
        }
        # Automatically add these params for CharFields
        if issubclass(self.serializer_class, serializers.CharField):
            serializer_kwargs['allow_blank'] = not self.schema.get('required')
            if self.schema.get('validate_max_length', True):
                try:
                    serializer_kwargs['max_length'] = int(self.schema.get('max_length'))
                except:
                    pass

        serializer_kwargs.update(self.get_extra_serializer_kwargs())
        return serializer_kwargs

    def create_serializer_field(self):
        """Create a DRF Serializer from the schema."""
        try:
            return self.serializer_class(**self.get_serializer_kwargs())
        except:
            logger.critical("[ContentField Data Error] Could not create Serializer from schema", exc_info=True)
            raise

    def adapt_schema_for_frontend(self):
        if self.is_prosemirror:
            self.schema['is_prosemirror'] = True
        if self.with_max_length:
            self.schema['is_textual'] = True
        self.further_adapt_schema_for_frontend()

    def further_adapt_schema_for_frontend(self):
        """
        Hook for subclasses : adapth the schema before sending it to the frontend
        """
        pass

    def validate_schema(self):
        """
        Validate the schema correctness (when created/edited)
        """
        # For now, we just check integer values
        errors = {}

        def _validate_int(property_name):
            if property_name in self.schema:
                try:
                    property_value = self.schema[property_name]
                    # Empty string or null
                    if not property_value:
                        del self.schema[property_name]
                    else:
                        self.schema[property_name] = int(property_value)
                except ValueError:
                    errors[property_name] = serializers.IntegerField.default_error_messages['invalid']

        if self.with_max_length:
            _validate_int('max_length')
        if self.with_min_value:
            _validate_int('min_value')
        if self.with_max_value:
            _validate_int('max_value')

        # Should we make extensive validation here ?
        # Like, "min_value is below max_value"

        if errors:
            raise ValidationError(errors)

    @classmethod
    def get_spec(cls):
        """
        Spec for the form builder
        """
        return {
            'type': cls.type,
            'label': force_text(cls.label),
            'description': force_text(cls.description),
            'can_be_required': cls.can_be_required,
            'can_be_elastic': cls.can_be_elastic,
            'with_initial': cls.with_initial,
            'with_placeholder': cls.with_placeholder,
            'with_max_length': cls.with_max_length,
            'with_validate_max_length': cls.with_validate_max_length,
            'with_min_value': cls.with_min_value,
            'with_max_value': cls.with_max_value,
            'with_choices': cls.with_choices,
            'with_regex': cls.with_regex
        }


CHAR_TYPE = 'char'
TEXT_TYPE = 'text'
PROSEMIRROR_TYPE = 'prosemirror'
ASSET_TYPE = 'asset'
EMAIL_TYPE = 'email'
INTEGER_TYPE = 'integer'
CHOICE_TYPE = 'choice'
RADIO_TYPE = 'radio'
MULTI_CHECKBOXES_TYPE = 'multi_checkboxes'
AUTO_COMPLETE_TYPE = 'auto_complete'
FACEBOOK_TYPE = 'facebook'
TWITTER_TYPE = 'twitter'

HELP_TEXT = 'help_text'

FILE_TYPE = 'file'


class BaseTextualField(ContentField):
    can_be_elastic = True
    with_placeholder = True
    with_max_length = True
    with_validate_max_length = True


class CharField(BaseTextualField):
    type = CHAR_TYPE
    label = _('Champ texte (une ligne)')
    description = _("Un champ texte simple, sur une seule ligne")
    serializer_class = serializers.CharField
    with_regex = True
    with_initial = True


class TextField(BaseTextualField):
    type = TEXT_TYPE
    label = _('Champ texte (multiligne)')
    description = _("Un champ texte (textarea) sur plusieurs lignes. Supporte uniquement le format texte, pas HTML")
    serializer_class = serializers.CharField
    with_initial = True


class ProsemirrorField(BaseTextualField):
    type = PROSEMIRROR_TYPE
    label = _('Editeur de texte')
    description = _("Editeur de texte riche avec mise en forme, annotations, etc ..")
    serializer_class = serializers.JSONField
    is_prosemirror = True


class AssetField(ContentField):
    class AssetSerializer(serializers.ModelSerializer):
        cover_url = serializers.CharField()
        file_url = serializers.CharField()
        id = serializers.IntegerField()
        name = serializers.CharField()
        working_urls = serializers.ListField(child=serializers.CharField())

        class Meta:
            model = Asset
            fields = (
                'cover_url',
                'extension',
                'file_url',
                'filetype',
                'id',
                'in_media_library',
                'name',
                'size',
                'version',
                'working_urls',
            )

    type = ASSET_TYPE
    label = _('Média')
    description = _("Un média")
    serializer_class = AssetSerializer


class EmailField(BaseTextualField):
    type = EMAIL_TYPE
    label = _('Email')
    description = _("Un champ de saisie avec validation spécifique pour les emails")
    serializer_class = serializers.EmailField
    can_be_elastic = True


class IntegerField(ContentField):
    type = INTEGER_TYPE
    label = _('Nombre entier')
    description = _("Un champ de saisie avec validation spécifique pour un nombre")
    serializer_class = serializers.IntegerField
    with_min_value = True
    with_max_value = True
    can_be_elastic = True

    def get_extra_serializer_kwargs(self):
        serializer_kwargs = {}
        try:
            serializer_kwargs['min_value'] = int(self.schema.get('min_value'))
        except:
            pass
        try:
            serializer_kwargs['max_value'] = int(self.schema.get('max_value'))
        except:
            pass
        return serializer_kwargs


class ChoiceField(ContentField):
    type = CHOICE_TYPE
    label = _('Menu déroulant')
    description = _("Menu déroulant à choix unique")
    serializer_class = serializers.ChoiceField
    with_choices = True

    def get_extra_serializer_kwargs(self):
        # Convert the multi-lang display into a plain string
        choices = self.schema.get('choices', [])
        for choice in choices:
            if isinstance(choice[1], dict):
                choice[1] = choice[1]['fr']
        return {
            'choices': choices
        }


class RadioField(ChoiceField):
    type = RADIO_TYPE
    label = _('Boutons Radios')
    with_choices = True


class MultiCheckboxesField(ContentField):
    type = MULTI_CHECKBOXES_TYPE
    label = _('Case à cocher multiples')
    description = _("Sélection multiples")
    serializer_class = serializers.JSONField
    with_choices = True


class AutoCompleteField(ContentField):
    type = AUTO_COMPLETE_TYPE
    label = _('Autocomplétion')
    description = _("Menu déroulant avec autocomplétion")
    serializer_class = serializers.CharField
    with_choices = True
    can_be_elastic = True


class HelpTextField(ContentField):
    type = HELP_TEXT
    label = _("Texte d'aide")
    description = _("Texte d'aide")
    serializer_class = serializers.CharField
    can_be_required = False


class FileField(ContentField):
    type = FILE_TYPE
    serializer_class = serializers.CharField
    can_be_required = False


class FacebookField(BaseTextualField):
    type = FACEBOOK_TYPE
    label = _('Editeur facebook')
    description = _("Editeur de texte avec validations spécifiques à Facebook")
    serializer_class = serializers.JSONField
    is_prosemirror = True

    def further_adapt_schema_for_frontend(self):
        self.schema['is_facebook'] = True


class TwitterField(BaseTextualField):
    type = TWITTER_TYPE
    label = _('Editeur twitter')
    description = _("Editeur de texte avec validations spécifiques à Twitter")
    serializer_class = serializers.JSONField
    is_prosemirror = True

    def further_adapt_schema_for_frontend (self):
        self.schema['is_twitter'] = True


CONTENT_FIELDS = (
    CharField,
    TextField,
    ProsemirrorField,
    AssetField,
    EmailField,
    IntegerField,
    ChoiceField,
    RadioField,
    MultiCheckboxesField,
    AutoCompleteField,
    FacebookField,
    TwitterField,
    HelpTextField
)
CONTENT_FIELDS_DICT = {content_field.type: content_field for content_field in CONTENT_FIELDS}

# This is merely a hack to continue to support the existing FileField
# which cannot be created anymore, but are still around in existing contents.
EXTENDED_CONTENT_FIELDS = CONTENT_FIELDS + (FileField, )
EXTENDED_CONTENT_FIELDS_DICT = {content_field.type: content_field for content_field in EXTENDED_CONTENT_FIELDS}


def create_content_field(field_schema):
    type = field_schema.get('type')
    if type not in EXTENDED_CONTENT_FIELDS_DICT:
        raise ValueError('Unknown content field type : "{}"'.format(type))
    content_field_class = EXTENDED_CONTENT_FIELDS_DICT[type]
    return content_field_class(field_schema)


def content_schema_to_content_fields(content_schema):
    return [create_content_field(field_schema) for field_schema in content_schema]


def get_content_schema_for_frontend(content_schema):
    content_schema = copy.deepcopy(content_schema)
    for field_schema in content_schema:
        content_field = create_content_field(field_schema)
        content_field.adapt_schema_for_frontend()
    return content_schema


def sanitize_content_schema(content_schema):
    content_schema = copy.deepcopy(content_schema)
    for field_schema in content_schema:
        if 'help_text' in field_schema:
            field_schema['help_text'] = sanitize_user_input_html(field_schema['help_text'])
    return content_schema


def get_content_field_specs():
    return [content_field.get_spec() for content_field in CONTENT_FIELDS]


def validate_field_schema(field_schema):
    try:
        content_field = create_content_field(field_schema)
    except ValueError as e:
        raise ValidationError(e)

    content_field.validate_schema()


def get_elastic_field_name(field_name, index):
    if index > 0:
        return "{}-{}".format(field_name, index)
    else:
        return field_name


def get_elastic_field_size(field_schema, content):
    i = 1  # Elastic size cannot be less than one
    while get_elastic_field_name(field_schema['name'], i) in content:
        i += 1
    return i







