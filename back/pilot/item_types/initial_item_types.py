import copy

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from pilot.item_types.models import ItemType


class InitialItemTypeNames:
    ARTICLE = 'Article'
    MEDIA = 'Media'
    TWITTER = 'Tweet'
    FACEBOOK = 'Statut Facebook'


TITLE_LABEL = {
    'fr': 'Titre',
    'en': 'Title'
}
TITLE_PLACEHOLDER = {
    'fr': 'Saisissez votre texte ici',
    'en': 'Type here'
}
BODY_LABEL = {
    'fr': 'Contenu',
    'en': 'Content'
}

TITLE_FIELD_SCHEMA = {
    'type': 'char',
    'name': 'title',
    'label': TITLE_LABEL['fr'],

    'required': False,
    'placeholder': TITLE_PLACEHOLDER['fr'],

    'show_in_creation': True,
    'show_in_public': True,
}

DEFAULT_CONTENT_SCHEMA = [TITLE_FIELD_SCHEMA]

ARTICLE_CONTENT_SCHEMA = [
    TITLE_FIELD_SCHEMA,
    {
        'type': 'prosemirror',
        'name': 'body',
        'label': BODY_LABEL['fr'],

        'required': False,

        'show_in_creation': False,
        'show_in_public': True,
    }
]

MEDIA_CONTENT_SCHEMA = [
    TITLE_FIELD_SCHEMA,
    {
        'type': 'asset',
        'name': 'media',
        'label': 'Media',

        'required': False,

        'show_in_creation': False,
        'show_in_public': True,
    }
]

TWITTER_CONTENT_SCHEMA = [
    TITLE_FIELD_SCHEMA,
    {
        'type': 'twitter',
        'name': 'body',
        'label': BODY_LABEL['fr'],

        'required': False,

        'max_length': settings.TWITTER_MAX_LENGTH,
        'validate_max_length': True,

        'show_in_creation': True,
        'show_in_public': True,
    },
]

FACEBOOK_CONTENT_SCHEMA = [
    TITLE_FIELD_SCHEMA,
    {
        'type': 'facebook',
        'name': 'body',
        'label': BODY_LABEL['fr'],

        'required': False,

        'show_in_creation': False,
        'show_in_public': True,
    },
]

MEDIA_DESCRIPTION = _("Avec ce type de contenu, ajoutez des PDFs ou des images en tant que contenu, et versionnez ou annotez-les ( comme du texte )")


def get_translated_field_schema(field_schema, lang='fr'):
    translated_schema = copy.deepcopy(field_schema)

    if translated_schema['name'] == 'title':
        translated_schema['label'] = TITLE_LABEL[lang]
        translated_schema['placeholder'] = TITLE_PLACEHOLDER[lang]
    if translated_schema['name'] == 'body':
        translated_schema['label'] = BODY_LABEL[lang]

    return translated_schema


def get_translated_content_schema(content_schema, lang='fr'):
    return [get_translated_field_schema(field_schema, lang) for field_schema in content_schema]


INITIAL_ITEM_TYPES = (
    dict(
        name=InitialItemTypeNames.ARTICLE,
        content_schema=ARTICLE_CONTENT_SCHEMA,
    ),
    dict(
        name=InitialItemTypeNames.MEDIA,
        content_schema=MEDIA_CONTENT_SCHEMA,
        description=MEDIA_DESCRIPTION
    ),
    dict(
        name=InitialItemTypeNames.TWITTER,
        content_schema=TWITTER_CONTENT_SCHEMA,
        icon_name='Twitter'
    ),
    dict(
        name=InitialItemTypeNames.FACEBOOK,
        content_schema=FACEBOOK_CONTENT_SCHEMA,
        icon_name='Facebook'
    ),
)


def init_item_types_for_desk(desk):
    for dict_state in INITIAL_ITEM_TYPES:
        ItemType.objects.create(desk=desk, created_by_id=1, **dict_state)
