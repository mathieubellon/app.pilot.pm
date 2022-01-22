import factory

from pilot.desks.models import Desk
from pilot.organizations import factories as organizations_factories


class DeskFactory(factory.DjangoModelFactory):
    """Base Desk factory."""
    FACTORY_FOR = Desk

    name = factory.Sequence("Desk{0}".format)
    organization = factory.SubFactory(organizations_factories.OrganizationFactory)
    created_by = factory.LazyAttribute(lambda desk: desk.organization.created_by)

    @classmethod
    def _prepare(cls, *args, **kwargs):
        from pilot.pilot_users.tests import factories as pilot_users_factories

        # Init a first user for the initial workflow states, if there isn't
        if not pilot_users_factories.models.PilotUser.objects.filter(id=1).exists():
            pilot_users_factories.PilotUserFactory.create(id=1)

        return super(DeskFactory, cls)._prepare(*args, **kwargs)

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        """
        Add optional users list, e.g.
            - DeskFactory.create(users=[user1, user2])
            - desk__users=[user1, user2]
        """
        # Add the user who created the organization to the users list.
        if not self.users.filter(pk=self.created_by.pk).exists():
            self.users.add(self.created_by)
        if extracted:
            # A list of users were passed in, use them.
            for user in extracted:
                self.users.add(user)
