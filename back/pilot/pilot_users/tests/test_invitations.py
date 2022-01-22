from django.test import TestCase

from pilot.pilot_users.models import InvitationToken
from pilot.pilot_users.tests import invitations_factories
from pilot.organizations import factories as organizations_factories




class FactoriesTests(TestCase):

    def test_invitation_token_factory(self):
        """Test InvitationTokenFactory."""
        invitation = invitations_factories.InvitationTokenFactory.create()

        self.assertIsNotNone(invitation.email)
        self.assertIsNotNone(invitation.organization)
        self.assertIsNotNone(invitation.permission)
        self.assertIsNotNone(invitation.token)
        self.assertIsNotNone(invitation.created_by)
        self.assertIsNotNone(invitation.created_at)
        self.assertIsNone(invitation.used_at)
        self.assertFalse(invitation.used)
        self.assertEqual(invitation.created_by, invitation.organization.created_by)


class InvitationTokenModelTests(TestCase):

    def test_unique_together_organization_token(self):
        """Test that organization and token fields are unique together."""

        organization = organizations_factories.OrganizationFactory.create()

        invitations = invitations_factories.InvitationTokenFactory.create_batch(
            size=20, organization=organization, token='toto')

        tokens = [invitation.token for invitation in invitations]

        self.assertFalse(len(tokens) > len(set(tokens)))  # Ensure all elements in the list are unique.

    def test_token_after_update(self):
        """Test that the token is not changed after an update."""

        # Create an invitation.
        invitation = invitations_factories.InvitationTokenFactory.create()
        first_token = invitation.token

        # Update the invitation.
        invitation.save()

        # Fetch the updated invitation.
        invitation = InvitationToken.objects.get(pk=invitation.pk)
        new_token = invitation.token

        # The token must still be the same.
        self.assertEqual(first_token, new_token)
