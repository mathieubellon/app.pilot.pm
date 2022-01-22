import factory

from pilot.organizations.models import Organization
from pilot.pilot_users.tests import factories as pilot_users_factories


class OrganizationFactory(factory.DjangoModelFactory):
    """Base Organization factory."""
    FACTORY_FOR = Organization

    name = factory.Sequence("Organization{0}".format)
    created_by = factory.SubFactory(pilot_users_factories.AdminFactory)

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        """
        Add optional users list, e.g.
            - OrganizationFactory.create(users=[user1, user2])
            - organization__users=[user1, user2]
        """
        # Add the user who created the organization to the users list.
        if not self.users.filter(pk=self.created_by.pk).exists():
            self.users.add(self.created_by)
        if extracted:
            # A list of groups were passed in, use them.
            for user in extracted:
                self.users.add(user)
