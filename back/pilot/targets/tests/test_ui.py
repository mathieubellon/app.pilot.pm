from django.test import TestCase
from django.urls import reverse

from pilot.desks.tests import factories as desks_factories
from pilot.utils.test import PilotAdminUserMixin

from pilot.targets.tests import factories as targets_factories


class FactoriesTests(TestCase):

    def test_target_factory(self):
        """Test TargetFactory."""
        target = targets_factories.TargetFactory.create()
        self.assertIsNotNone(target.desk)
        self.assertEqual(target.created_by, target.desk.created_by)



class TargetsUiTest(PilotAdminUserMixin, TestCase):
    def setUp(self):
        super(TargetsUiTest, self).setUp()
        # Keep a reference to the list view URL.
        self.targets_list_url = reverse('ui_targets_admin')

    def tearDown(self):
        # Delete all Target objects after each test.
        Target.objects.all().delete()

    def test_targets_list(self):
        """Test targets list."""

        targets = targets_factories.TargetFactory.create_batch(size=10, desk=self.desk)

        # Test GET.
        response = self.client.get(self.targets_list_url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(targets), len(response.context['targets']))

    def test_target_add(self):
        """Test target add."""

        url = reverse('ui_target_add')

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        post_data = {
            'name': 'Target 1',
            'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.targets_list_url)

        # Check added Target.
        target = Target.objects.get(name=post_data['name'])
        self.assertEqual(target.desk, self.desk)
        self.assertEqual(target.created_by, self.user)

        # The just added Target must appears in the targets list.
        response = self.client.get(self.targets_list_url)
        self.assertIn(target, response.context['targets'])

    def test_target_edit(self):
        """Test target edit."""

        target = targets_factories.TargetFactory.create(desk=self.desk)
        url = reverse('ui_target_edit', kwargs={'target_pk': target.pk, })

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        post_data = {
            'name': 'Edited Target 2',
            'description': 'New description.',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.targets_list_url)

        # Check edited Target.
        target = Target.objects.get(pk=target.pk)
        self.assertEqual(target.desk, self.desk)
        self.assertEqual(target.name, post_data['name'])
        self.assertEqual(target.description, post_data['description'])
        self.assertEqual(target.updated_by, self.user)

    def test_target_delete(self):
        """Test target delete."""

        target = targets_factories.TargetFactory.create(desk=self.desk)
        url = reverse('ui_target_delete', kwargs={'target_pk': target.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.targets_list_url)

        # The Target should have been deleted.
        self.assertEqual(Target.objects.all().count(), 0)

    def test_targets_perms(self):
        """Test targets perms."""

        # Create another desk for another user.
        other_desk = desks_factories.DeskFactory.create()

        # Create a target related to the other desk.
        other_target = targets_factories.TargetFactory.create(desk=other_desk)

        # Test list, it should be empty because the logged user has no targets.
        response = self.client.get(self.targets_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, len(response.context['targets']))

        # Test edit perms. The other target should not be accessible.
        url = reverse('ui_target_edit', kwargs={'target_pk': other_target.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # Test delete perms. The other target should not be accessible.
        url = reverse('ui_target_delete', kwargs={'target_pk': other_target.pk})
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 404)

        self.client.logout()

        # Log the other user in.
        self.client.login(email=other_desk.created_by.email, password='password')

        # The other user can edit the target.
        url = reverse('ui_target_edit', kwargs={'target_pk': other_target.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # The other user can delete the target.
        url = reverse('ui_target_delete', kwargs={'target_pk': other_target.pk})
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 302)

        self.client.logout()
