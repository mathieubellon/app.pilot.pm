from django.conf import settings

from pilot.item_types import item_content_fields

SIMPLE_TEST_SCHEMA = [
    {
        'type': item_content_fields.INTEGER_TYPE,
        'name': 'integer',
        'label': 'test label',
        'help_text': 'test help text'
    },
    {
        'type': item_content_fields.CHAR_TYPE,
        'name': 'char'
    },
    {
        'type': item_content_fields.EMAIL_TYPE,
        'name': 'email'
    },
]

ADVANCED_TEST_SCHEMA = SIMPLE_TEST_SCHEMA + [
    {
        'type': item_content_fields.CHAR_TYPE,
        'name': 'title',
        'max_length': 200,
        'remaining_char': True,
        'validate_max_length': False
    },
    {
        'type': item_content_fields.PROSEMIRROR_TYPE,
        'name': 'body',
        'label': 'Contenu',
        'required': False,
    },
]

VALIDATION_TEST_SCHEMA = [
    # ==============================
    # Required char field
    # ==============================
    {
        'type': item_content_fields.CHAR_TYPE,
        'name': 'char',
        'label': 'Char',
        'required': True
    },

    # ==============================
    # Twitter post (280 char)
    # ==============================

    {
        'type': item_content_fields.PROSEMIRROR_TYPE,
        'name': 'twitter',
        'label': 'Twitter',
        'required': False,
        'tooltip': 'mini',
        'is_twitter': True,
        'max_length': settings.TWITTER_MAX_LENGTH,
        'validate_max_length': True,
        'remaining_char': True
    },

    # ==============================
    # Integer with min/max
    # ==============================
    {
        'type': item_content_fields.INTEGER_TYPE,
        'name': 'integer',
        'label': 'integer',
        "required": False,
        "max_value": 5,
        "min_value": 1
    },
]
