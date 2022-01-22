from django.core import mail
from django.urls import reverse
from django.test import TestCase

from pilot.pilot_users.tests import factories as pilot_users_factories



class RegistrationsUiTest(TestCase):

    def setUp(self):
        # Init a first user for the initial workflow states, if there isn't
        if not PilotUser.objects.filter(id=1).exists():
            pilot_users_factories.PilotUserFactory.create(id=1)

    def test_registration_process(self):

        url = reverse('ui_registration')

        # 1) Test GET.

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 2a) Test POST with password length <= MIN_PASSWORD_LENGTH.

        post_data = {
            'email': 'FOO@LOCALHOST.COM',
            'first_name': 'John',
            'last_name': 'Doe',
            'organization': 'John Doe Ltd.',
            'password1': 'p',
            'password2': 'p',
            'username': 'JohnDoe',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "caractères minimum")

        # 2b) Test POST with password length > MIN_PASSWORD_LENGTH.

        post_data = {
            'email': 'FOO@LOCALHOST.COM',
            'first_name': 'John',
            'last_name': 'Doe',
            'organization': 'John Doe Ltd.',
            'password1': 'password',
            'password2': 'password',
            'username': 'JohnDoe',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_registration_done'))

        # 3) Test created objects.

        user = PilotUser.objects.get(email=post_data['email'].lower())
        # Ensure the user has only one group.
        self.assertEqual(1, user.groups.all().count())
        # Ensure that the user email is in lower case (EmailLowerCaseField should be used in the Form).
        self.assertEqual(user.email, post_data['email'].lower())
        # Ensure the user is in the admin group.
        self.assertIn(PERMISSION_ADMINS, user.groups.all().values_list('name', flat=True))
        # Ensure the user is inactive.
        self.assertFalse(user.is_active)

        organization = Organization.objects.get(name=post_data['organization'])
        self.assertEqual(user, organization.created_by)
        self.assertEqual(1, organization.users.all().count())

        desk = Desk.objects.get(created_by=user)
        self.assertEqual(1, organization.users.all().count())
        self.assertEqual(organization, desk.organization)

        token_url = user.get_token_url('ui_registration_confirm')
        self.assertEqual(len(mail.outbox), 1, "A confirmation email must have been sent")
        self.assertIn(token_url, mail.outbox[0].body)

        # Ensure the user is not logged in.
        self.assertIsNone(self.client.session.get('_auth_user_id'))

        # 4) Test email confirmation.

        response = self.client.get(token_url)
        self.assertEqual(response.status_code, 302)

        # Refresh the cached user instance.
        user = PilotUser.objects.get(pk=user.pk)

        # Ensure the user is now active.
        self.assertTrue(user.is_active)

        # The new user should be automatically logged in.
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        self.client.logout()
