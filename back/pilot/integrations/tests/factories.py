import factory

from pilot.desks.tests import factories as desks_factories
from pilot.integrations.models import ApiToken


class ApiTokenFactory(factory.DjangoModelFactory):
    """Channel Token factory"""
    FACTORY_FOR = ApiToken

    desk = factory.SubFactory(desks_factories.DeskFactory)

    @factory.post_generation
    def channels(self, create, extracted, **kwargs):
        if extracted:
            for channel in extracted:
                self.channels.add(channel)
