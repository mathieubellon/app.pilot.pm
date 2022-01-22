import factory

from pilot.pilot_users.models import InvitationToken


class InvitationTokenFactory(factory.DjangoModelFactory):
    """Base InvitationToken factory."""
    FACTORY_FOR = InvitationToken

    email = factory.Sequence("ras.poutine{0}@example.com".format)
    created_by = factory.LazyAttribute(lambda invitation_token: invitation_token.organization.created_by)
