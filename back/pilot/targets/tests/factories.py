import factory

from pilot.desks.tests import factories as desks_factories
from pilot.targets.models import Target


class TargetFactory(factory.DjangoModelFactory):
    """Base Target factory."""
    FACTORY_FOR = Target

    desk = factory.SubFactory(desks_factories.DeskFactory)
    name = factory.Sequence("Target{0}".format)
    description = "Lorem ipsum dolor sit amet"
    created_by = factory.LazyAttribute(lambda target: target.desk.created_by)
