# Generated by Django 2.1.7 on 2019-06-11 08:39
import json

from django.db import migrations
from django.db.models import Count

from pilot.utils import noop
from pilot.utils.models import serialize_model_instance


EDIT_SESSION_CONTENT_TYPE_ID = 21


def take_snapshot(item_type, ItemTypeSnapshot):
    serialized_data = serialize_model_instance(item_type, ('updated_at'))
    # The creator of the snapshot is the last updater of the item
    # If we create the first snapshot, there won't be any item updater, so use the creator
    creator = item_type.updated_by or item_type.created_by
    # Save the snapshot
    return ItemTypeSnapshot.objects.create(
        item_type=item_type,
        created_by=creator,
        serialized_data=serialized_data
    )


def migrate_snapshots_content_schema(apps, schema_editor):
    ItemSnapshot = apps.get_model("items", "ItemSnapshot")
    ItemType = apps.get_model("item_types", "ItemType")
    ItemTypeSnapshot = apps.get_model("item_types", "ItemTypeSnapshot")
    Desk = apps.get_model("desks", "Desk")
    Activity = apps.get_model("activity_stream", "Activity")
    Notification = apps.get_model("notifications", "Notification")

    # 1/ When there's multiple snapshots of the same version, keep only the most recent
    mulitple_snapshots = (ItemSnapshot.objects
        .values('item_id', 'major_version', 'minor_version')
        .annotate(total=Count('item_id'))
        .order_by('item_id')
        .filter(total__gt=1)
    )

    for mulitple_snapshot in mulitple_snapshots.iterator():
        snapshot_to_keep = ItemSnapshot.objects.filter(
            item_id=mulitple_snapshot['item_id'],
            major_version=mulitple_snapshot['major_version'],
            minor_version=mulitple_snapshot['minor_version'],
        ).only('id').latest()

        snapshots_to_delete = ItemSnapshot.objects.filter(
            item_id=mulitple_snapshot['item_id'],
            major_version=mulitple_snapshot['major_version'],
            minor_version=mulitple_snapshot['minor_version'],
        ).exclude(id=snapshot_to_keep.id)

        # Reassign the generic foreign key to the snapshot id that we keep
        snapshots_ids_to_delete = list(snapshots_to_delete.values_list('id', flat=True))
        Activity.objects.filter(
            target_content_type_id=EDIT_SESSION_CONTENT_TYPE_ID,
            target_object_id__in=snapshots_ids_to_delete
        ).update(
            target_object_id=snapshot_to_keep.id
        )
        Activity.objects.filter(
            action_object_content_type_id=EDIT_SESSION_CONTENT_TYPE_ID,
            action_object_object_id__in=[str(id) for id in snapshots_ids_to_delete]
        ).update(
            action_object_object_id=snapshot_to_keep.id
        )
        Notification.objects.filter(
            on_object_contenttype_id=EDIT_SESSION_CONTENT_TYPE_ID,
            on_object__in=snapshots_ids_to_delete
        ).update(
            on_object=snapshot_to_keep.id
        )

        snapshots_to_delete.delete()

    # 2/ Some old ItemType had no ItemTypeSnapshot created, init them now
    for item_type in ItemType.objects.annotate(snapshots_count=Count('snapshots')).filter(snapshots_count=0):
        take_snapshot(item_type, ItemTypeSnapshot)

    # 3/ Now that we narrowed down the number of ItemSnapshot
    # we want to find their item_type_snapshot corresponding to their schema
    for desk in Desk.objects.all():
        item_type_snapshots = {}
        for item_type_snapshot in ItemTypeSnapshot.objects.filter(item_type__desk_id=desk.id):
            schema = item_type_snapshot.serialized_data.get('fields', {}).get('content_schema', [])
            serialized_schema = json.dumps(schema, sort_keys=True)
            item_type_snapshots[serialized_schema] = item_type_snapshot

        for snapshot in ItemSnapshot.objects.filter(item__desk_id=desk.id).iterator():
            serialized_schema = json.dumps(snapshot.content_schema, sort_keys=True)
            item_type_snapshot = item_type_snapshots.get(serialized_schema)

            if not item_type_snapshot:
                item_type = snapshot.item.item_type
                serialized_data = serialize_model_instance(item_type, ('updated_at', 'content_schema'))
                serialized_data['fields']['content_schema'] = snapshot.content_schema
                item_type_snapshot = ItemTypeSnapshot.objects.create(
                    item_type_id=item_type.id,
                    created_at=item_type.created_at,
                    created_by=item_type.updated_by or item_type.created_by,
                    serialized_data=serialized_data
                )
                item_type_snapshots[serialized_schema] = item_type_snapshot

            snapshot.item_type_snapshot = item_type_snapshot
            # Also migrate the start/end date
            snapshot.start = snapshot.created_at
            snapshot.end = snapshot.created_at
            # Also init the editors array
            snapshot.editors = [snapshot.created_by_id]
            snapshot.save()


def migrate_review_items(apps, schema_editor):
    Review = apps.get_model("items", "Review")

    for review in Review.objects.select_related('item_snapshot', 'item_snapshot__item').iterator():
        review.item = review.item_snapshot.item
        review.save()


class Migration(migrations.Migration):

    dependencies = [
        # We need to migrate the comments before removing the duplicate ItemSnapshots
        ('comments', '0002_migrate_comments'),
        ('items', '0009_auto_20190611_1030'),
    ]

    operations = [
        migrations.RunPython(migrate_snapshots_content_schema, reverse_code=noop),
        migrations.RunPython(migrate_review_items, reverse_code=noop),
    ]
