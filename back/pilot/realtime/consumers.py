import logging
import copy

from autobahn.exception import Disconnected
from channels.generic.websocket import JsonWebsocketConsumer
from django.shortcuts import get_object_or_404

from pilot.desks.utils import get_current_desk, connect_to_desk
from pilot.items.models import Item
from pilot.sharings.models import Sharing
from pilot.realtime.broadcasting import broadcaster, sync_group_discard, sync_group_add
from pilot.realtime.items import ItemContentUpdater
from pilot.realtime.messages import C2S_MESSAGES, get_desk_group, get_item_group, S2C_MESSAGES
from pilot.realtime.store import store, RealtimeUser

from pilot.utils.perms import filter_items_for_sharing

logger = logging.getLogger(__name__)


class PilotConsumer(JsonWebsocketConsumer):
    """
    Our main consumer that handle realtime operations on the Items.

    Users may be authenticated ( internal user ) or not ( public user, with item sharing )
    """
    def connect(self):
        self.user = None
        self.desk_group_name = None
        self.item_group_name = None

        dj_user = self.scope['user']
        session = self.scope['session']

        if dj_user.is_authenticated:
            desk = get_current_desk(dj_user, session)
            if desk:
                connect_to_desk(
                    desk=desk,
                    user=dj_user,
                    session=session
                )
                self.desk_group_name = get_desk_group(desk.id)
                sync_group_add(self.desk_group_name, self.channel_name)

            self.user = RealtimeUser(self, dj_user=dj_user)
            store.add_user(self.user)

        self.accept()

        user_id = self.user.id if self.user else 'anonymous'
        logger.info(f"[Realtime] User connected user_id={user_id}")

    def disconnect(self, close_code):
        if self.user:
            store.remove_user(self.user)
            broadcaster.broadcast_users_on_item(self.user.item_id)

        if self.desk_group_name:
            sync_group_discard(self.desk_group_name, self.channel_name)
        if self.item_group_name:
            sync_group_discard(self.item_group_name, self.channel_name)

        user_id = self.user.id if self.user else 'anonymous'
        logger.info(f"[Realtime] User disconnected user_id={user_id}")

    def receive_json(self, message):
        try:
            # Keep our user alive
            if self.user:
                self.user.breath()
            type = message.get('type')

            # Auth call will not have a connected user...
            if type == C2S_MESSAGES.SHARED_ITEM_AUTH:
                self.shared_item_auth(message)

            # ...but every other calls should have one !
            elif self.user is None:
                return

            if type == C2S_MESSAGES.REGISTER_ON_ITEM:
                self.register_on_item(message)
            elif type == C2S_MESSAGES.UPDATE_USER_ACTIVITY:
                self.update_user_activity(message)
            elif type == C2S_MESSAGES.UPDATE_ITEM_CONTENT:
                self.update_item_content(message)
            elif type == C2S_MESSAGES.DELETE_ELASTIC_ELEMENT:
                self.delete_elastic_element(message)
        except:
            logger.exception(f'Error during receive.\nMessage:{message}\n', exc_info=True)

    # ===================
    # Inbound messages
    # ===================

    def shared_item_auth(self, message):
        """
        Public users must authenticate with a token before using the realtime API
        """
        token = message.get('token')
        sharing = get_object_or_404(Sharing, token=token)
        self.user = RealtimeUser(self, sharing=sharing)
        store.add_user(self.user)

        logger.info(f"[Realtime] External user auth user_id={sharing.email}")

    def register_on_item(self, message):
        """
        Client will call this API when they start working on an Item
        """
        if not self.user:
            return

        try:
            item_id = int(message.get('item_id'))
        except:
            return

        item_queryset = Item.objects.filter(id=item_id)

        # For authenticated users, ensure that the user has access to this item
        if self.user.dj_user:
            if not item_queryset.filter_by_permissions(self.user.dj_user).exists():
                return

        # For anonymous users, ensure that the auth is valid,
        # And that the sharing give access to this item
        else:
            if not filter_items_for_sharing(item_queryset, self.user.sharing).exists():
                return

        store.register_user_on_item(self.user, item_id)
        self.item_group_name = get_item_group(item_id)
        sync_group_add(self.item_group_name, self.channel_name)

        broadcaster.broadcast_users_on_item(self.user.item_id)

    def update_user_activity(self, message):
        """
        Keep track of user activity between field focus, field updating and selection (on prosemirror fields)
        """
        updated_user = message['user']

        # Limit updating to those attributes
        for attr in ['field_focus', 'field_updating', 'selection']:
            if attr in updated_user:
                setattr(self.user, attr, updated_user[attr])

        broadcaster.broadcast_users_on_item(self.user.item_id)

    def update_item_content(self, message):
        """
        Main API for live edit : receive the atomic changes created by the users
        """
        if not self.user.item_id:
            return

        # from pprint import pformat
        # message_copy = copy.deepcopy(message)
        # del message_copy['changes']['body']['value']
        # formatted = pformat(message_copy, width=120)
        # print(f"===== MESSAGE RECEIVED FROM {self.user.id} ====\n]{formatted}")

        update_result = ItemContentUpdater(self.user.id, self.user.item_id).apply_changes(message['changes'])

        # Update the selection after propagating the change, and only if they were accepted
        if update_result['accepted']:
            self.user.selection = message.get('selection')
            broadcaster.broadcast_users_on_item(self.user.item_id)

        # If there's an invalid change, inform the emitter
        if update_result['invalid']:
            self.send_json({
                'type': S2C_MESSAGES.INVALID_CHANGES,
                'changes': update_result['invalid']
            })


    def delete_elastic_element(self, message):
        """
        Specific API to deal with elastic field element deletion
        """
        if not self.user.item_id:
            return

        item_content_updater = ItemContentUpdater(self.user.id, self.user.item_id)
        item_content_updater.delete_elastic_element(
            field_name=message['field_name'],
            index=message['index']
        )

    # ===================
    # Passthough messages from broadcaster
    # ===================

    def broadcast(self, message):
        """
        Transmit messages send from the broadcaster to the final client ( see broadcasting.py )
        """
        # It's critical to make a copy here,
        # because the same message dict will be passed around to different consumers
        message = copy.copy(message)
        exclude_recipients = message.pop('exclude_recipients')
        if self.user.id in exclude_recipients:
            return
        message['type'] = message.pop('actual_type')

        try:
            self.send_json(message)
        except Disconnected:
            # The websocket has been disconnected, we cannot broadcast
            pass
