import arrow
import copy
import logging

from django.core.exceptions import FieldDoesNotExist
from django.db.models import FileField, BooleanField
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.db.models.fields import DateTimeField, DateField
from django.utils.translation import ugettext_lazy as _

from diff_match_patch import diff_match_patch

from pilot.item_types.item_content import ItemContentMixin
from pilot.item_types.item_content_fields import get_content_schema_for_frontend
from pilot.items.models import Item

logger = logging.getLogger(__name__)


diff_match_patch_api = diff_match_patch()


EXCLUDED_DIFFING_FIELDS = [
    'updated_at',
    'updated_by',
    'created_at',
    # json content (from ItemContentMixin) will be handled separatly by
    # the dedicated item_content_diff function
    'json_content',
    # Don't diff the search fields
    'search_vector',
    'partial_search_document',
    # Internal fields on Item
    'annotations',
    'last_edition_datetime',
    'last_editor',
]

JSON_CONTENT_FIELD_NAME = 'json_content'


def format_field_diff_for_api(field_diff, content_type):
    field_name = field_diff.get('field_name')

    # Special handling for ItemContent,
    # which doesn't show the diff inline, but should redirect to the session url
    if field_name == JSON_CONTENT_FIELD_NAME:
        return {
            'field_name': JSON_CONTENT_FIELD_NAME,
            'field_label': _('Contenu')
        }

    field_type = None
    field_label = field_name

    if content_type:
        try:
            field = content_type.model_class()._meta.get_field(field_name)
            field_type = field.get_internal_type()
            field_label = field.verbose_name
        except FieldDoesNotExist:
            # The most probable cause here is a migration which removed a field.
            # We cannot do much about it, so just emit a warning so someone can check.
            logger.warning(
                f"Cannot format a diff for API because a field is missing :\n"
                f"content_type : {content_type}\n"
                f"field_name : {field_name}",
                exc_info=True
            )

    return {
        'field_name': field_name,
        'field_type': field_type,
        'field_label': field_label,
        'before': field_diff.get('before'),
        'after': field_diff.get('after')
    }


def format_diff_for_api(diff, content_type):
    diff_data = []
    for field_diff in (diff or []):
        try:
            diff_data.append(format_field_diff_for_api(
                field_diff=field_diff,
                content_type=content_type
            ))
        except Exception as e:
            field_name = field_diff.get('field_name', '')
            logger.error(
                f"format_diff_for_api formatting failed for ContentType {content_type} on field '{field_name}'",
                exc_info=True
            )
            diff_data.append({
                'field_name': field_name,
                'error': _('Erreur interne')
            })

    return diff_data


def format_field_diff_as_text(instance_or_model, field_diff):
    field_name = field_diff.get('field_name')
    try:
        field = instance_or_model._meta.get_field(field_name)
    except FieldDoesNotExist:
        # The most probable cause here is a migration which removed a field.
        # We cannot do much about it, so just emit a warning so someone can check.
        logger.warning(
            "Cannot format an Activity's diff as text because a field is missing :\n"
            "instance_or_model : {}\n"
            "field_name : {}".format(instance_or_model, field_name),
            exc_info=True
        )
        return {
            'field_name': field_name,
            'field_label': field_name,
            'html_diff': _("An error has occured"),
        }

    before = field_diff['before']
    after = field_diff['after']
    text_diff = None

    # Special handling for m2m
    if isinstance(field, ManyToManyField):
        m2m_diff = []
        set_before = set([(related_diff['id'], related_diff['repr']) for related_diff in before])
        set_after = set([(related_diff['id'], related_diff['repr']) for related_diff in after])

        for id, repr in set_before.difference(set_after):
            m2m_diff.append('- {}'.format(repr))

        for id, repr in set_after.difference(set_before):
            m2m_diff.append('+ {}'.format(repr))

        text_diff = '\n'.join(m2m_diff)

    # For ForeignKey, retrieve the representation of the related instance
    elif isinstance(field, ForeignKey):
        # In the case of a migration which changed the field to ForeignKey,
        # the before version won't be a dict
        if isinstance(before, dict):
            before = before.get('repr', '')
        if isinstance(after, dict):
            after = after.get('repr', '')

    # Ignore time in DateTimeField, its never actually used by the end-user
    elif isinstance(field, DateField) or isinstance(field, DateTimeField):
        before = before and arrow.get(before).format('DD/MM/YYYY')
        after = after and arrow.get(after).format('DD/MM/YYYY')

    # Ignore time in DateTimeField, its never actually used by the end-user
    elif isinstance(field, BooleanField):
        before = _('Oui') if before else _('Non')
        after = _('Oui') if after else _('Non')

    # Standard handling for other fields
    if not text_diff:
        text_diff = '{} -> {}'.format(before or '∅', after or '∅')

    return {
        'field_name': field_name,
        'field_label': field.verbose_name,
        'text_diff': text_diff,
    }


def format_diff_as_text(instance_or_model, diff):
    text_diff = ""
    for field_diff in diff:
        formatted = format_field_diff_as_text(instance_or_model, field_diff)
        text_diff += f"{formatted['field_label']} : {formatted['text_diff']}\n"
    return text_diff


def item_content_diff(old_item_content, new_item_content, only_changed_fields=False):
    """
    Compare item content stored as json dict.
    """
    diff_data = {}
    content_schema = []
    new_item_converters = new_item_content.converters or {}
    old_item_converters = old_item_content.converters or {}

    field_names = list(old_item_converters.keys())
    for i, right_name in enumerate(new_item_converters.keys()):
        if right_name not in field_names:
            field_names.insert(i, right_name)

    for field_name in field_names:
        try:
            field_message = None
            old_value = None
            new_value = None
            old_converter = old_item_converters.get(field_name)
            new_converter = new_item_converters.get(field_name)
            old_field_schema = old_item_content.get_field_schema(field_name)
            new_field_schema = new_item_content.get_field_schema(field_name)

            # Nothing to compare ?!?
            if not old_converter and not new_converter:
                continue
            if not old_field_schema and not new_field_schema:
                continue

            content_schema.append(new_field_schema if new_field_schema else old_field_schema)
            ref_converter = new_converter if new_converter else old_converter
            is_prosemirror = ref_converter.is_prosemirror

            if old_converter:
                old_value = old_converter.value

            if new_converter:
                new_value = new_converter.value

            # Will happens when the ItemType is edited to add a field
            if new_converter and not old_converter:
                field_message = _('Champ créé')
                old_value = ''

            # Will happens when the ItemType is edited to remove a field
            elif old_converter and not new_converter:
                field_message = _('Champ supprimé')
                new_value = ''

            # We can't compare the fields if their type aren't equal.
            # Will happen when the ItemType is edited by removing a field, and recreate it with another type
            if old_converter and new_converter and old_converter.content_field.type != new_converter.content_field.type:
                field_message = _('Le type du champ a changé entre les deux versions. Impossible de montrer les différences.')
        except:
            logger.error(f"Error while diffing field {field_name}", exc_info=True)
            field_message = _('Erreur interne lors du diff')

        if only_changed_fields and (old_value == new_value) and not field_message:
            continue

        diff_data[field_name] = {
            'old_value': old_value,
            'new_value': new_value,
            'is_prosemirror': is_prosemirror,
            'message': field_message
        }

    return {
        'diff': diff_data,
        'content_schema': content_schema
    }


def item_content_diff_for_frontend(left, right):
    # The left version must always be before the right version, swap them if it's not the case
    swapped = False
    if left.created_at > right.created_at:
        left, right = right, left
        swapped = True

    content_diff = item_content_diff(
        old_item_content=left,
        new_item_content=right,
    )
    return {
        'diff': content_diff['diff'],
        'content_schema': get_content_schema_for_frontend(content_diff['content_schema']),
        'swapped': swapped,
        'version': {
            'left': getattr(left, 'version', '?'),
            'right': getattr(right, 'version', '?'),
        }
    }


class DiffTracker(object):
    """
    A class that help generating a diff for an instance update.

    Generate a list of field_diff object, which have the following format :
    {
        'field_name': 'name',
        'before': value_before,
        'after': value_after
    }
    """
    def __init__(self, instance_before):
        self.instance_before = copy.deepcopy(instance_before)
        self.m2m_before = {}
        # Fetch M2M before any update is done, so we have a correct picture of the data before
        for field in instance_before._meta.many_to_many:
            self.m2m_before[field.name] = list(getattr(self.instance_before, field.name).all())

        self.model = type(instance_before)

    def get_diff(self, instance_after):
        diff_data = []

        # json content (from ItemContent) is a special case that should be handled at display time
        if issubclass(self.model, ItemContentMixin):
            content_diff = item_content_diff(
                old_item_content=self.instance_before,
                new_item_content=instance_after,
                only_changed_fields=True
            )['diff']

            # If there's any updated content field,
            # Store a special marker for it
            if content_diff:
                diff_data.append({
                    'field_name': JSON_CONTENT_FIELD_NAME
                })

        for field in self.model._meta.fields + self.model._meta.many_to_many:
            if field.name in EXCLUDED_DIFFING_FIELDS:
                continue

            before = getattr(self.instance_before, field.name)
            after = getattr(instance_after, field.name)

            # Related fields are a special case we have to handle separately
            # to store more informations.
            if isinstance(field, ManyToManyField):
                before = [self.format_diff_for_related_instance(related) for related in self.m2m_before.get(field.name, [])]
                after = [self.format_diff_for_related_instance(related) for related in after.all()]

            if isinstance(field, ForeignKey):
                before = self.format_diff_for_related_instance(before)
                after = self.format_diff_for_related_instance(after)

            # Ignore fields which are equal
            if before == after:
                continue

            # Retrieve the representation of fields with choices
            if field.choices:
                before = dict(field.choices).get(before)
                after = dict(field.choices).get(after)

            elif isinstance(field, DateField) or isinstance(field, DateTimeField):
                before = before and before.isoformat()
                after = after and after.isoformat()

            # Retrieve the representation of state fields
            if isinstance(field, FileField):
                before = before.url
                after = after.url

            diff_data.append({
                'field_name': field.name,
                'before': before,
                'after': after
            })

        return diff_data

    def format_diff_for_related_instance(self, related_instance):
        if related_instance is None:
            return {
                'id': None,
                'repr': ''
            }
        else:
            return {
                'id': related_instance.id,
                'repr': str(related_instance)
            }

