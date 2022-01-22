from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import TestCase

from pilot.utils.test import PNG_IMG_FILE, PilotAdminUserMixin, PilotRestrictedEditorUserMixin


class DeskUiTest(PilotAdminUserMixin, TestCase):
    def test_desk_edit(self):
        """Test desk edition."""

        url = reverse('ui_desk_edit')

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 1) Update the profile with a raw logo.
        post_data = {
            'name': 'My desk',
            'logo': SimpleUploadedFile('logo.png', PNG_IMG_FILE.decode('base64'), 'image/png'),
            'color': '#000000',

        }

        desk = self.user.desks.all()[0]
        self.assertNotEqual(desk.name, post_data['name'])
        self.assertNotEqual(desk.color, post_data['color'])

        # Test POST.
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url)

        # Refresh the cached desk instance.
        desk = self.user.desks.all()[0]

        self.assertEqual(desk.name, post_data['name'])
        self.assertEqual(desk.color, post_data['color'])

        # Test logo.
        self.assertIn('{0}.png'.format(desk.id), desk.logo.name)
        self.assertTrue(default_storage.exists(desk.logo.name))

        # 2) Update the profile without new raw logo.
        post_data = {
            'name': 'My new desk',
            'logo': '',
            'color': '#ffffff',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url)

        # Refresh the cached desk instance.
        desk = self.user.desks.all()[0]

        # Test logo still exists.
        self.assertIsNotNone(desk.logo.name)
        # Test logo dimensions, it should have been resized via the thumbnail() method.
        self.assertEqual(desk.logo.width, Desk.LOGO_SIZE[0])
        self.assertEqual(desk.logo.height, Desk.LOGO_SIZE[1])

        # 3) Update the desk with a new default tab.

        post_data = {
            'name': 'My new desk',
            'logo': '',
            'color': '#ffffff'
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url)

        # Refresh the cached desk instance.
        desk = self.user.desks.all()[0]
        # Delete logo at the end of the test.
        default_storage.delete(desk.logo.name)


class NotAdminDeskUiTest(PilotRestrictedEditorUserMixin, TestCase):
    def test_desk_cant_edit(self):
        """Test non admin user cannot edit desk."""

        url = reverse('ui_desk_edit')

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
