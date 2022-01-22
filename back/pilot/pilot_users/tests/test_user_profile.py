from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import TestCase

from pilot.pilot_users.tests import factories as pilot_users_factories
from pilot.utils.test import PNG_IMG_FILE, PilotAdminUserMixin


class UserProfileUiTest(PilotAdminUserMixin, TestCase):
    def test_user_profile_edit(self):
        """Test account edition."""

        url = reverse('ui_user_profile_edit')

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 1) Update the profile with a raw avatar.
        post_data = {
            'email': 'NEW@NEW.COM',
            'first_name': 'Henry',
            'last_name': 'Ford',
            'username': 'HenryFord',
            'avatar': SimpleUploadedFile('avatar.png', PNG_IMG_FILE.decode('base64'), 'image/png'),
            'phone': '0123456789',
            'localization': 'Somewhere',
            'job': 'CEO',
        }

        # Ensure that the email is in lower case (EmailLowerCaseField should be used in the Form).
        self.assertNotEqual(self.user.email, post_data['email'].lower())
        self.assertNotEqual(self.user.first_name, post_data['first_name'])
        self.assertNotEqual(self.user.last_name, post_data['last_name'])
        self.assertNotEqual(self.user.username, post_data['username'])
        self.assertNotEqual(self.user.phone, post_data['phone'])
        self.assertNotEqual(self.user.localization, post_data['localization'])
        self.assertNotEqual(self.user.job, post_data['job'])

        # Test POST.
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url)

        # Refresh the cached self.user instance.
        self.user = PilotUser.objects.get(pk=self.user.pk)

        self.assertEqual(self.user.email, post_data['email'].lower())
        self.assertEqual(self.user.first_name, post_data['first_name'])
        self.assertEqual(self.user.last_name, post_data['last_name'])
        self.assertEqual(self.user.username, post_data['username'])
        self.assertEqual(self.user.phone, post_data['phone'])
        self.assertEqual(self.user.localization, post_data['localization'])
        self.assertEqual(self.user.job, post_data['job'])

        # Test avatar.
        self.assertIn('{0}.png'.format(self.user.id), self.user.avatar.name)
        self.assertTrue(default_storage.exists(self.user.avatar.name))

        # 2) Update the profile without new raw avatar.
        post_data = {
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.first_name,
            'username': 'NewHenryFord',
            'avatar': '',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url)

        # Refresh the cached self.user instance.
        self.user = PilotUser.objects.get(pk=self.user.pk)

        # Test avatar still exists.
        self.assertIsNotNone(self.user.avatar.name)
        # Test avatar dimensions, it should have been resized via the thumbnail() method.
        self.assertEqual(self.user.avatar.width, PilotUser.AVATAR_SIZE[0])
        self.assertEqual(self.user.avatar.height, PilotUser.AVATAR_SIZE[1])

        # Delete avatar at the end of the test.
        default_storage.delete(self.user.avatar.name)

    def test_user_profile_edit_username(self):
        """Test uniqueness of the username."""

        # Create another user with the username 'toto'.
        pilot_users_factories.EditorFactory.create(password='password', username='toto')

        url = reverse('ui_user_profile_edit')
        post_data = {
            'username': 'TOto',  # Try to use an already existing username with a different case.
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('username', response.context['form'].errors, "This username should already exists.")

    def test_password_change(self):
        """Test password change."""

        # Change password with length below MIN_PASSWORD_LENGTH.
        post_data = {
            'old_password': 'password',
            'new_password1': 'p',
            'new_password2': 'p',
        }
        response = self.client.post(reverse('auth_password_change'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "caractères minimum")

        # Change password with password at correct length.
        post_data = {
            'old_password': 'password',
            'new_password1': 'new_password',
            'new_password2': 'new_password',
        }
        response = self.client.post(reverse('auth_password_change'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('auth_password_change_done'))
        self.client.logout()

        # User can log in with his new password.
        self.assertTrue(self.client.login(email=self.user.email, password='new_password'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)
        self.client.logout()
