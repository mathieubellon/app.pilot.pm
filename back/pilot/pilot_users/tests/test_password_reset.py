from django.core import mail
from django.urls import reverse
from django.test import TestCase

from pilot.pilot_users.tests import factories as pilot_users_factories



class PasswordResetUiTest(TestCase):
    def test_password_reset(self):
        # Request a password change.
        user = pilot_users_factories.EditorFactory.create()
        post_data = {
            'email': user.email,
        }
        response = self.client.post(reverse('auth_password_reset'), post_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('auth_password_reset_done'))

        # Change forgotten password.
        token_url = user.get_token_url('auth_password_reset_confirm')

        # Test with password length below MIN_PASSWORD_LENGTH setting (6)
        post_data = {
            'new_password1': 'p',
            'new_password2': 'p',
        }
        response = self.client.post(token_url, data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "caractères minimum")

        # Test with password length above MIN_PASSWORD_LENGTH setting (6)
        post_data = {
            'new_password1': 'new_password',
            'new_password2': 'new_password',
        }
        response = self.client.post(token_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('auth_password_reset_complete'))

        # The user can now log in with his new password.
        self.assertTrue(self.client.login(email=user.email, password='new_password'))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        self.client.logout()
