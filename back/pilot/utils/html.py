import json
import bleach
from bleach.callbacks import nofollow, target_blank
from rest_framework.compat import SHORT_SEPARATORS
from rest_framework.utils.encoders import JSONEncoder
from webpack_loader import utils as webpack_loader_utils

ALLOWED_TAGS = ['ul', 'ol', 'li', 'strong', 'em']
ALLOWED_ATTRIBUTES = []
ALLOWED_STYLES = []


LINKIFY_CALLBACKS = [nofollow, target_blank]


def sanitize_user_input_html(text):
    return bleach.clean(
        text=text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        styles=ALLOWED_STYLES
    )


def linkify_user_input(text):
    return bleach.linkify(text, LINKIFY_CALLBACKS, parse_email=True)


def sanitize_and_linkify(text):
    return linkify_user_input(sanitize_user_input_html(text))


def render_json(value):
    """ Render a python primitive type (dict, list...) as a json usable in html template"""
    return json.dumps(
        value,
        cls=JSONEncoder,
        ensure_ascii=False,
        separators=SHORT_SEPARATORS
    )


def get_webpack_bundle_name():
    return webpack_loader_utils.get_files('main', 'js')[0]['name']
