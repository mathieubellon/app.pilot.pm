import datetime
import random
from cacheout import LRUCache

from django.conf import settings
from django.utils import timezone

user_colors = [
    '#911eb4',
    '#008080',
    '#ff7700',
    '#e61f1f',
    '#3cb44b',
    '#ffaa00',
    '#8859F7',
    '#4363d8',
    '#d66b67',
]

# 5 minutes the testing in local dev
if settings.DEBUG:
    BREATHING_TIME_BEFORE_DEATH = datetime.timedelta(minutes=5)
# 30 minutes in production
else:
    BREATHING_TIME_BEFORE_DEATH = datetime.timedelta(minutes=30)

class RealtimeUser(object):
    """
    Represent a user connected to our server through a websocket.

    It may be a internal user, with a django User instance associated.
    Or a public user ( via an item sharing ), in which case we'll use its email as an id.

    Each user have a living time, and will be disconnected after a period of inactivity.
    Users must breath to be kept alive, which is done at each message received from him.
    """
    def __init__(self, consumer, dj_user=None, sharing=None):
        if dj_user:
            self.id = dj_user.id
            # The django db model instance
            self.dj_user = dj_user
            self.email = None
        elif sharing:
            self.id = sharing.email
            self.dj_user = None
            self.email = sharing.email
        else:
            raise ValueError("RealtimeUser must be initialized with a django user or an email")

        # For anonymous users, keep a reference to the sharing object that give them access to the server
        self.sharing = sharing

        # The django-channel Consumer instance through this user is connected to the realtime server
        self.consumer = consumer
        # The timestamp of the last activity of this user
        self.last_breathing = timezone.now()
        # The item id where the user is currently connected
        self.item_id = None
        # The field name the user is currently focused id
        self.field_focus = None
        # The selection in a tiptap field
        self.selection = None
        # The field name the user is currently updating
        self.field_updating = None
        # The color of the user on the registered item
        self.color = None

    def breath(self):
        self.last_breathing = timezone.now()

    def is_dead(self):
        return timezone.now() - self.last_breathing > BREATHING_TIME_BEFORE_DEATH

    def to_dict(self):
        user_dict = {
            'id': self.id,
            'color': self.color,
            'field_focus': self.field_focus,
            'selection': self.selection,
            'field_updating': self.field_updating
        }
        if self.dj_user:
            user_dict.update({
                'username': self.dj_user.username,
                'avatar': self.dj_user.get_avatar_url()
            })
        else:
            user_dict.update({
                'username': self.email,
                'avatar': None
            })

        return user_dict


class Store():
    """
    Keep track of all users connected to the realtime server,
    and which user is registered on which item.
    """
    def __init__(self):
        # userId => RealtimeUser
        # self.users = LRUCache(
        #     maxsize=4096,
        #     ttl=0,
        # )
        # itemId -> set([RealtimeUser, ...])
        self.users_on_item = LRUCache(
            maxsize=4096,
            ttl=0,
            default=lambda key: set()
        )

    def add_user(self, user):
        pass
        # self.users.set(user.id, user)

    def remove_user(self, user):
        # self.users.delete(user.id)
        if user.item_id and user.item_id in self.users_on_item:
            self.users_on_item.get(user.item_id).discard(user)

    def get_users_on_item(self, item_id):
        return self.users_on_item.get(item_id, [])

    def register_user_on_item(self, user, item_id):
        user.item_id = item_id
        users_on_this_item = self.users_on_item.get(item_id)

        used_colors = [user.color for user in users_on_this_item]
        for color in random.sample(user_colors, len(user_colors)):
            if color not in used_colors:
                user.color = color
                break

        users_on_this_item.add(user)

    def eliminate_dead_connections(self, item_id):
        dead_connections = []
        # Make a copy of the set, so we d'ont run into concurrent edition issues
        for user in list(self.users_on_item.get(item_id)):
            if user.is_dead():
                self.remove_user(user)
                dead_connections.append(user)
        return dead_connections


store = Store()
