from django.db import transaction
from django.utils import timezone

from pilot.activity_stream.jobs import create_activity
from pilot.activity_stream.models import Activity
from pilot.items.models import Item
from pilot.utils import states
from pilot.utils.projel.hierarchy import ensure_consistent_hierarchy, projels_for_item

DEFAULT_COPY_PARAMS = {
    'items': True,
    'owners': True,
    'channels': True,
    'targets': True,
    'assets': True,
    'metadata': True,
    'tags': True
}

PROJECT_COPY_METADATA_FIELDS = (
    'description',
    'priority',
    'category',
)

PROJECT_COPY_M2M_FIELDS = (
    'owners',
    'channels',
    'targets',
    'assets',
    'tags',
)

ITEM_COPY_METADATA_FIELDS = (
    'project',
    'item_type',
    'json_content',
    'language',
    'is_private',
    'in_trash',
)

ITEM_COPY_M2M_FIELDS = (
    'channels',
    'owners',
    'targets',
    'assets',
    'tags',
)


def copy_field(source, destination, field_name):
    setattr(destination, field_name, getattr(source, field_name))


def copy_m2m_field(source, destination, field_name):
    getattr(destination, field_name).set(getattr(source, field_name).all())


def copy_fields(source, destination, metadata_fields, m2m_fields):
    for metadata_field_name in metadata_fields:
        copy_field(source, destination, metadata_field_name)

    # We need an id to set m2m fields, so create the object into the db if it does not exists already
    if not destination.pk:
        destination.save()

    for m2m_field_name in m2m_fields:
        copy_m2m_field(source, destination, m2m_field_name)


def copy_item(item, created_by,
              metadata_fields=ITEM_COPY_METADATA_FIELDS,
              m2m_fields=ITEM_COPY_M2M_FIELDS,
              **kwargs):
    new_item = Item(
        desk=item.desk,
        created_by=created_by,
        updated_by=created_by,
        last_editor=created_by.id,
        last_edition_datetime=timezone.now(),
        copied_from=item,
        **kwargs
    )
    copy_fields(item, new_item, metadata_fields, m2m_fields)
    new_item.save()

    # Initial activity
    create_activity(
        actor=created_by,
        desk=item.desk,
        verb=Activity.VERB_COPIED,
        target=new_item,
        action_object=item
    )

    # Here we don't use the HierarchyConsistencyJob,
    # because we need to update the hierarchy in a sync way,
    # so ProjelDetailHierarchy.vue can reload the hierarchy immediately
    for projel in projels_for_item(new_item):
        ensure_consistent_hierarchy(projel)


def copy_project(source_project, new_project, copy_params={}):
    """
    Copy a project into a new project.

    The copy_params parameter allow to turn on/off the data to copy :
     - metadata
     - items
     - owners
     - channels
     - targets
     - assets
    """
    with transaction.atomic():
        should_copy = DEFAULT_COPY_PARAMS.copy()
        should_copy.update(copy_params or {})

        # Items copy
        if should_copy['items']:
            # We want to erase the original project, to reassign it to the newly created project
            item_metadata_fields = [field_name for field_name in ITEM_COPY_METADATA_FIELDS if field_name != 'project']
            for item in source_project.items.filter(hidden=False).order_by('updated_at'):
                copy_item(
                    item=item,
                    created_by=new_project.created_by,
                    metadata_fields=item_metadata_fields,
                    project=new_project  # assign to the new project
                )

        metadata_fields = PROJECT_COPY_METADATA_FIELDS if should_copy['metadata'] else []
        m2m_fields = [field_name for field_name in PROJECT_COPY_M2M_FIELDS if should_copy[field_name]]
        copy_fields(source_project, new_project, metadata_fields, m2m_fields)
        new_project.state = states.STATE_ACTIVE
        new_project.save()

        ensure_consistent_hierarchy(new_project)

        # Initial activity
        create_activity(
            actor=new_project.created_by,
            desk=new_project.desk,
            verb=Activity.VERB_COPIED,
            target=new_project,
            action_object=source_project
        )
