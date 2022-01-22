import factory

from pilot.channels.models import Channel
from pilot.desks.tests import factories as desks_factories


class ChannelFactory(factory.DjangoModelFactory):
    """Base Channel factory."""
    FACTORY_FOR = Channel

    desk = factory.SubFactory(desks_factories.DeskFactory)
    name = factory.Sequence("Channél{0}".format)
    description = "Channel lorem îpsum dolor sit amet"
    created_by = factory.LazyAttribute(lambda channel: channel.desk.organization.created_by)

    @factory.post_generation
    def owners(self, create, extracted, **kwargs):
        if extracted:
            for user in extracted:
                self.owners.add(user)
