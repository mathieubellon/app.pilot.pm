from aioredis import ConnectionClosedError
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from pilot.assets.api.serializers import AssetSerializer
from pilot.items.api.light_serializers import EditSessionLightSerializer, serialize_editor
from pilot.items.api.serializers import ItemSerializer
from pilot.items.models import EditSession, Item
from pilot.realtime.messages import S2C_MESSAGES, get_desk_group, get_item_group
from pilot.realtime.store import store

# ===================
# Outbound messages (broadcasting)
# ===================

channel_layer = get_channel_layer()
sync_group_add = async_to_sync(channel_layer.group_add)
sync_group_send = async_to_sync(channel_layer.group_send)
sync_group_discard = async_to_sync(channel_layer.group_discard)


class Broadcaster:
    """
    Entry-point for broadcasting messages to multiple clients through websockets.

    Broadcasting in django-channels is a bit special because we can't communicate directly with the clients.
    We need to send a message to each consumer attached to the client we want to reach,
    and the consumer will then transmit the message itself.

    The message we want to send has a "type" parameter, but django-channels also use this name for routing the messages.
    We use an "actual_type" parameter here, which will be converted to "type" by the consumer upon sending to the client.
    """

    def broadcast(self, group_name, type, exclude_recipients=[], **data):
        """
        Low-level API for broadcasting, not for direct use outside this class.
        """
        data.update({
            'type': 'broadcast',
            'actual_type': type,
            'exclude_recipients': exclude_recipients
        })
        try:
            sync_group_send(group_name, data)
        except ConnectionClosedError:
            pass

    def broadcast_asset_conversion_status(self, asset):
        self.broadcast(
            group_name=get_desk_group(asset.desk_id),
            type=S2C_MESSAGES.BROADCAST_ASSET_CONVERSION_STATUS,
            asset=AssetSerializer(asset).data
        )

    def broadcast_users_on_item(self, item_id):
        """
        Broadcast the list of users connected to an item, and their selection/field status.
        """
        # remove stall connections before broadcasting the users
        dead_connections = store.eliminate_dead_connections(item_id)
        users = store.get_users_on_item(item_id)
        self.broadcast(
            group_name=get_item_group(item_id),
            type=S2C_MESSAGES.BROADCAST_USERS_ON_ITEM,
            users=[user.to_dict() for user in users]
        )
        # Close the connection AFTER broadcasting the "users_on_item" message,
        # So the frontend has the time to update its disconnection message
        for user in dead_connections:
            user.consumer.close()

    def broadcast_item(self, item_id, sender_id=None, **extra_data):
        """
        Broadcast the full item representation, after an update on something else than the content.
        """
        # Fetch a fresh Item instance, so the serializer have up to date data for its nested serializers
        # which may have been updated.
        item = Item.objects.detail_api_prefetch().get(id=item_id)

        session = EditSession.objects.filter(item_id=item_id).latest()
        self.broadcast(
            group_name=get_item_group(item.id),
            type=S2C_MESSAGES.BROADCAST_ITEM,
            item=ItemSerializer(item).data,
            exclude_recipients=[sender_id],
            session=EditSessionLightSerializer(session).data,
            **extra_data
        )

    def broadcast_item_changes(self, item_id, editor, changes):
        """
        Broadcast atomic changes on the item content, which are created during live edit.
        """
        session = EditSession.objects.filter(item_id=item_id).latest()
        self.broadcast(
            group_name=get_item_group(item_id),
            type=S2C_MESSAGES.BROADCAST_ITEM_CHANGES,
            changes=changes,
            session=EditSessionLightSerializer(session).data,
            editor=serialize_editor(editor)
        )

broadcaster = Broadcaster()
