from django.test import TestCase

from pilot.pilot_users.tests import factories as pilot_users_factories



class FactoriesTests(TestCase):
    def test_pilot_user_factory(self):
        """Test PilotUserFactory."""
        user = pilot_users_factories.PilotUserFactory.create(password='password')
        self.assertEqual(0, user.groups.all().count())
        self.assertFalse(user.permissions.is_admin)
        self.assertFalse(user.permissions.is_editor)
        self.assertFalse(user.permissions.is_restricted_editor)
        self.assertTrue(self.client.login(email=user.email, password='password'))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        self.client.logout()

    def test_admin_factory(self):
        """Test AdminFactory."""
        user = pilot_users_factories.AdminFactory.create(password='password')
        self.assertEqual(1, user.groups.all().count())
        self.assertTrue(user.permissions.is_admin)
        self.assertFalse(user.permissions.is_editor)
        self.assertFalse(user.permissions.is_restricted_editor)
        self.assertTrue(self.client.login(email=user.email, password='password'))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        self.client.logout()

    def test_editor_factory(self):
        """Test EditorFactory."""
        user = pilot_users_factories.EditorFactory.create(password='password')
        self.assertEqual(1, user.groups.all().count())
        self.assertFalse(user.permissions.is_admin)
        self.assertTrue(user.permissions.is_editor)
        self.assertFalse(user.permissions.is_restricted_editor)
        self.assertTrue(self.client.login(email=user.email, password='password'))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        self.client.logout()

    def test_restricted_editor_factory(self):
        """Test RestrictedEditorFactory."""
        user = pilot_users_factories.RestrictedEditorFactory.create(password='password')
        self.assertEqual(1, user.groups.all().count())
        self.assertFalse(user.permissions.is_admin)
        self.assertFalse(user.permissions.is_editor)
        self.assertTrue(user.permissions.is_restricted_editor)
        self.assertTrue(self.client.login(email=user.email, password='password'))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        self.client.logout()
