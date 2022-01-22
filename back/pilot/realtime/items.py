import copy
import datetime
import json
import arrow

from django.conf import settings
from django.db import transaction

from pilot.activity_stream.jobs import create_activity
from pilot.activity_stream.models import Activity
from pilot.item_types.item_content_fields import get_elastic_field_name
from pilot.items.models import Item
from pilot.notifications import notify
from pilot.realtime.broadcasting import broadcaster
from pilot.utils.diff import DiffTracker

# 30 seconds for the testing in local dev
if settings.DEBUG:
    BREAK_TIME_BETWEEN_SESSIONS = datetime.timedelta(seconds=30)
# 15 minutes in production
else:
    BREAK_TIME_BETWEEN_SESSIONS = datetime.timedelta(minutes=15)


class ItemContentUpdater:
    """
    Apply atomic changes on the item, and keep everything tidy :
    - Field history
    - Field versions
    - Annotations
    - EditSessions

    There's also method for the special case of elastic field element deletion.
    """
    def __init__(self, user_id, item_id):
        self.user_id = user_id
        self.item_id = item_id
        self.item = None
        self.diff_tracker = None

    def apply_changes(self, changes):
        update_result = dict(
            accepted={},
            invalid={},
            rejected={},
        )
        any_content_change_accepted = False

        timestamp = arrow.utcnow().isoformat()

        ##############################################################
        # Start of transaction with the select_for_update, lock acquired
        ##############################################################

        # select_for_update in a transaction to guard against concurrent editing.
        # This will serve as a lock around the synchronized code block, until we end the transaction
        with transaction.atomic():
            item = self.item = Item.objects.with_content().select_for_update().get(id=self.item_id)
            self.diff_tracker = DiffTracker(item)
            annotations_before = copy.deepcopy(item.annotations)

            for field_name, change in changes.items():
                add_elastic_element = change.get('action') == 'addElasticElement'

                if add_elastic_element:
                    base_field_name = field_name[:field_name.rfind('-')]
                    content_field = item.get_content_field(base_field_name)
                else:
                    content_field = item.get_content_field(field_name)

                # The field name does not match a field on the item type schema
                if not content_field:
                    continue

                # Ensure the version is correct
                current_version = item.field_versions.setdefault(field_name, 0)
                if current_version != change.get('version'):
                    update_result['rejected'][field_name] = change
                    continue

                # The version is correct and the content is valid, we accept the change
                change['timestamp'] = timestamp
                # The change has been accepted, we can increase the version number
                item.field_versions[field_name] = current_version + 1
                change['version'] = current_version + 1

                # Annotations-only changes won't have a value
                if 'value' in change:
                    value = change['value']

                    # Special-case to ensure no oversized base64-encoded image ever reach the server,
                    # which would wreak havoc in cascade to a lot of service ( queue, redis, database... )
                    if content_field.is_prosemirror:
                        serialized_value = json.dumps(value)
                        if 'data:image' in serialized_value and 'base64,' in serialized_value:
                            update_result['invalid'][field_name] = 'base64'
                            continue

                    item.content[field_name] = value
                    any_content_change_accepted = True

                # For prosemirror fields, if there's steps,
                # we don't need to store the field value in the history
                if 'steps' in change:
                    change.pop('value', None)

                if 'annotations' in change:
                    if item.annotations is None:
                        item.annotations = {}
                    annotations_key = change.get('annotationsKey', field_name)
                    item.annotations[annotations_key] = change['annotations']

                update_result['accepted'][field_name] = change

            # We save the item only if there's accepted change
            if update_result['accepted']:
                item.last_editor = self.user_id
                item.last_edition_datetime = timestamp
                if isinstance(self.user_id, int):
                    item.updated_by_id = self.user_id
                item.updated_at = timestamp
                item.save()

                # Update the session only for content changes, not annotations
                if any_content_change_accepted:
                    self.update_session(timestamp)

        ##############################################################
        # End of transaction with the select_for_update, lock released
        ##############################################################

        annotations_after = item.annotations
        notify.process_notifications_when_annotation_is_updated(
            item,
            annotations_before,
            annotations_after
        )

        # If any change(s) has been accepted, we must publish for broadcast
        if update_result['accepted']:
            broadcaster.broadcast_item_changes(self.item_id, self.user_id, update_result['accepted'])

        return update_result

    def delete_elastic_element(self, field_name, index):
        # select_for_update in a transaction to guard against concurrent editing.
        # This will serve as a lock around the synchronized code block, until we end the transaction
        with transaction.atomic():
            item = self.item = Item.objects.select_for_update().get(id=self.item_id)
            self.diff_tracker = DiffTracker(item)

            i = index
            while get_elastic_field_name(field_name, i+1) in item.content:
                old_name = get_elastic_field_name(field_name, i+1)
                new_name = get_elastic_field_name(field_name, i)
                new_value = item.content[old_name]
                item.content[new_name] = new_value
                item.annotations[new_name] = item.annotations.get(old_name, {})
                item.field_versions[new_name] += 1
                i+=1

            last_field_name = get_elastic_field_name(field_name, i)
            item.content.pop(last_field_name, None)
            item.annotations.pop(last_field_name, None)

            item.save()
            self.update_session(arrow.utcnow().isoformat())

        broadcaster.broadcast_item(self.item_id)

    def create_session(self, timestamp):
        session = self.item.create_session(
            timestamp=timestamp,
            created_by_id=self.user_id if isinstance(self.user_id, int) else None
        )

        create_activity(
            # Internal user, or external email
            actor=session.created_by if isinstance(self.user_id, int) else self.user_id,
            desk=self.item.desk,
            verb=Activity.VERB_STARTED_EDIT_SESSION,
            target=self.item,
            action_object=session,
            diff=self.diff_tracker.get_diff(self.item),
        )

        return session

    def get_current_session(self, timestamp):
        # First change ever, we need to create a session
        if self.item.sessions.count() == 1:
            return self.create_session(timestamp)
        # There's already somme session, check if we're using the same or must create a new one
        else:
            last_session = self.item.last_session
            last_edit_time = last_session.end

            # Last edit is too old, ceate a new session
            if arrow.get(timestamp) - arrow.get(last_edit_time) > BREAK_TIME_BETWEEN_SESSIONS:
                return self.create_session(timestamp)
            # We're still in the same session
            else:
                return last_session

    def update_session(self, timestamp):
        current_session = self.get_current_session(timestamp)
        current_session.content = self.item.content
        current_session.annotations = self.item.annotations
        current_session.end = timestamp
        if self.user_id not in current_session.editors:
            current_session.editors.append(self.user_id)
        if isinstance(self.user_id, int):
            current_session.updated_by_id = self.user_id
        current_session.save()
