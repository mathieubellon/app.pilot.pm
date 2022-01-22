from pilot.desks.models import Desk
from pilot.items.models import Item
from pilot.utils.test import EMPTY_PROSEMIRROR_DOC, prosemirror_body
from pilot.item_types.tests.testing_item_type_definition import VALIDATION_TEST_SCHEMA

from pilot.items.tests import factories as items_factories
from pilot.projects.tests import factories as projects_factories
from pilot.channels.tests import factories as channel_factories
from pilot.targets.tests import factories as targets_factories
from pilot.pilot_users.tests import factories as pilot_users_factories
from pilot.item_types.tests import factories as item_types_factories


LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit"

def empty_item():
    desk = Desk.objects.first()

    # Init an empty item with a general type
    items_factories.ItemFactory.create(
        desk=desk,
        json_content={
            'title': 'Awesome title',  # Start with initial title
            'body': EMPTY_PROSEMIRROR_DOC
        }
    )

def content_validation():
    desk = Desk.objects.first()

    item_type = item_types_factories.ItemTypeFactory.create(
        desk=desk,
        content_schema=VALIDATION_TEST_SCHEMA
    )
    items_factories.ItemFactory.create(
        desk=desk,
        item_type=item_type,
        json_content={
            'char': 'abc'
        }
    )

def review():
    desk = Desk.objects.first()
    channel = channel_factories.ChannelFactory(name="Review Channel")
    project = projects_factories.ProjectFactory(name="Review Project")

    items_factories.ItemFactory.create(
        desk=desk,
        json_content={
            'title': 'Review title',  # Start with initial title
            'body': prosemirror_body(LOREM_IPSUM)
        },
        channel=channel,
        project=project
    )

def informations():
    desk = Desk.objects.first()

    targets_factories.TargetFactory.create_batch(size=5, desk=desk)
    channel_factories.ChannelFactory.create_batch(size=5, desk=desk)
    projects_factories.ProjectFactory.create_batch(size=5, desk=desk)
    users = pilot_users_factories.PilotUserFactory.create_batch(size=5)
    desk.users.add(*users)


    items_factories.ItemFactory.create(
        desk=desk,
        channel=None
    )
