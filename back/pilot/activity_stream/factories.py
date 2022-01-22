import factory

from pilot.activity_stream.models import Activity
from pilot.desks.tests import factories as desks_factories
from pilot.items.tests import factories as items_factories
from pilot.pilot_users.tests import factories as pilot_users_factories


class ActivityFactory(factory.DjangoModelFactory):
    """Base Activity factory."""
    FACTORY_FOR = Activity

    desk = factory.SubFactory(desks_factories.DeskFactory)
    actor = factory.SubFactory(pilot_users_factories.EditorFactory)
    action_object = factory.SubFactory(items_factories.ConfirmedItemFactory, desk=factory.SelfAttribute('..desk'))
