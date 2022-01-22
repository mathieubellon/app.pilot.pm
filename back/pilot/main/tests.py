import datetime

from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.test import TestCase
from pilot.utils.test import PilotAdminUserMixin

from pilot.items.tests import factories as items_factories


class LoginTest(PilotAdminUserMixin, TestCase):
    def tearDown(self):
        # Delete all Item objects after each test.
        Item.all_the_objects.all().delete()

    def test_login_view(self):
        login_url = reverse('auth_login')
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 200)

        self.client.logout()

        # We fill the form without checking the `remember me` checkbox.
        post_data = {'username': self.user.email, 'password': 'password'}
        response = self.client.post(login_url, data=post_data)
        self.assertRedirects(response, reverse('dashboard'))
        # The session must expire when the browser is closed
        self.assertTrue(self.client.session.get_expire_at_browser_close())

        self.client.logout()

        # We fill the form and we check the `remember me` checkbox.
        post_data = {'username': self.user.email, 'password': 'password', 'remember_me': 'on'}
        response = self.client.post(login_url, data=post_data)
        self.assertRedirects(response, reverse('dashboard'))

        # The session must stay alive when the browser is closed.
        self.assertFalse(self.client.session.get_expire_at_browser_close())

        # We compute a timedelta object from the settings
        cookie_age_delta = datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE)
        # We compute a timedelta beetween now and the expiry date in the session
        expiry_date = self.client.session.get_expiry_date()
        delta = expiry_date - timezone.now()

        # The difference beetween the 2 computed deltas must be small (we choosed 10 seconds, but usually less than 1)
        self.assertTrue(cookie_age_delta - delta <= datetime.timedelta(seconds=10))

    def test_login_view_redirect(self):
        """ Test redirection after loggin """
        # First, we create an item
        item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk,
            in_trash=True
        )
        item_url = reverse('ui_item_details', kwargs={'item_pk': item.pk})

        # the we send to the login view the related "next" parameter
        login_url = reverse('auth_login')
        post_data = {'username': self.user.email, 'password': 'password', 'next': item_url}
        response = self.client.post(login_url, data=post_data, follow=True)
        self.assertRedirects(response, reverse('ui_item_details', kwargs={'item_pk': item.pk}))
        # Finally, we make sure we are on the expected item detail page

        self.assertContains(response, '<div id="vue-item-detail"></div>')
        self.assertContains(response, 'itemId: %s' % item.pk)
