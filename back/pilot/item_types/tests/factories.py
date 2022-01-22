import factory
import copy

from pilot.desks.tests import factories as desks_factories
from pilot.item_types import initial_item_types
from pilot.item_types.models import ItemType


class ItemTypeFactory(factory.DjangoModelFactory):
    """ Factory for ItemType."""
    FACTORY_FOR = ItemType

    desk = factory.SubFactory(desks_factories.DeskFactory)
    created_by = factory.LazyAttribute(lambda item: item.desk.organization.created_by)
    name = factory.Sequence("Custôm typé name {0}".format)
    description = factory.Sequence("Descrïptîon {0}".format)
    content_schema = factory.LazyAttribute(lambda x: copy.deepcopy(initial_item_types.ARTICLE_CONTENT_SCHEMA))
