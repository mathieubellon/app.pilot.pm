from django.test import TestCase

from pilot.organizations import factories as organizations_factories
from pilot.pilot_users.tests import factories as pilot_users_factories




class FactoriesTests(TestCase):

    def test_organization_factory(self):
        """Test OrganizationFactory."""

        organization = organizations_factories.OrganizationFactory.create()

        self.assertIn(organization.created_by, organization.users.all())
        self.assertIsNotNone(organization.updated_at)

    def test_organization_factory_with_users(self):
        """Test OrganizationFactory with additional users."""

        editor = pilot_users_factories.EditorFactory.create()
        restricted_editor = pilot_users_factories.RestrictedEditorFactory.create()

        organization = organizations_factories.OrganizationFactory.create(users=[editor, restricted_editor])

        # The creator of the organization should have been automatically created.
        self.assertIn(organization.created_by, organization.users.all())

        # Number of users = organization's creator + editor + restricted_editor.
        self.assertEqual(3, organization.users.all().count())
