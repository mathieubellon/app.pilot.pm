import os
import datetime

from django.contrib.contenttypes.models import ContentType
from pilot.activity_stream.models import Activity
from pilot.assets.models import Asset, AssetRight
from pilot.channels.models import Channel
from pilot.comments.models import Comment
from pilot.item_types.models import ItemType, ItemTypeSnapshot
from pilot.items.models import Item, EditSession
from pilot.itemsfilters.models import SavedFilter, PublicSharedFilter
from pilot.labels.models import Label
from pilot.notifications.models import Notification
from pilot.pilot_users.models import Team, PilotUser, UserInOrganization, UserInDesk, UserInDeskDeactivated
from pilot.projects.models import Project
from pilot.targets.models import Target
from pilot.tasks.models import Task, TaskGroup
from pilot.workflow.models import WorkflowState


class ModelConfig(object):
    def __init__(self, model, desk_attr='desk'):
        self.model = model
        self.desk_attr = desk_attr


MC = ModelConfig
# The model will be deserialized in the order specified in this list,
# which is obviously critical for correct FK referencing
DEMO_MODELS = [
    MC(ContentType, None),
    MC(Team),
    MC(PilotUser, 'desks'),
    MC(UserInOrganization, 'user__desks'),
    MC(UserInDesk),
    MC(UserInDeskDeactivated),
    MC(Label),
    MC(Channel),
    MC(Target),
    MC(ItemType),
    MC(ItemTypeSnapshot, 'item_type__desk'),
    MC(WorkflowState),
       
    MC(Asset),
    MC(AssetRight),
    MC(Project),
    MC(Item),
    MC(EditSession, 'item__desk'),
    MC(SavedFilter),
    MC(PublicSharedFilter, 'saved_filter__desk'),

    MC(TaskGroup),
    MC(Task),

    MC(Comment),
    MC(Notification),
    MC(Activity),
]

DUMP_DIRECTORY = os.path.join(os.path.dirname(__file__), 'dump')

ANCHOR_DATE = datetime.date(2020, 6, 5)


def get_dump_path(basename):
    return os.path.join(DUMP_DIRECTORY, basename + '.json')


def get_dump_path_for_model(model):
    return get_dump_path(model._meta.model_name)


SUBSCRIPTION_PLAN_DUMP_PATH = get_dump_path('subscriptionplan')
DESK_DUMP_PATH = get_dump_path('desk')
ORGANIZATION_DUMP_PATH = get_dump_path('organization')
USERS_DUMP_PATH = get_dump_path('pilotuser')
TEAMS_DUMP_PATH = get_dump_path('team')


