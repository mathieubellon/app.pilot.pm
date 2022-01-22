import json
import time
from unittest.case import skip

from django.conf import settings
from django.core import mail
from django.urls import reverse
from django.db.models import Min, Max
from django.http import QueryDict
from django.test import TestCase
from django.utils import timezone

from pilot.projects.tests import factories as projects_factories
from pilot.items.tests import factories as items_factories
from pilot.item_types import initial_item_types
from pilot.items.api import filters as items_filters
from pilot.pilot_users.tests import factories as pilot_users_factories
from pilot.utils.test import PilotAdminUserMixin

from pilot.utils.selenium_test import SeleniumTest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import urllib.parse as urlparse

class CustomListItemsUiTest(PilotAdminUserMixin, TestCase):
    """Test custom lists of Item objects."""

    def setUp(self):
        super(CustomListItemsUiTest, self).setUp()
        # Keep a reference to the list view URL.
        self.main_items_list_url = reverse('ui_items_list')

    def tearDown(self):
        # Delete all Item objects after each test.
        Item.objects.all().delete()

    @skip("SharedFilter has been moved to an API")
    def test_save_custom_list(self):
        """Save a custom list from the main list view."""

        url = self.main_items_list_url
        post_data = {
            'title': 'Custom list',
            'query': 'page=1&page_size=15&total_pages=1&total_entries=1&project=1&start=2014-01-01&end=2014-01-31',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)

        saved_filter = SavedFilter.objects.get(title=post_data['title'])

        self.assertEqual(saved_filter.title, post_data['title'])
        self.assertEqual(saved_filter.query, post_data['query'])
        self.assertEqual(saved_filter.type, SavedFilter.TYPE_LIST)

        self.assertRedirects(response, reverse('ui_saved_filter', kwargs={'filter_pk': saved_filter.pk}))

    @skip("SharedFilter has been moved to an API")
    def test_edit_custom_list(self):
        """Display and edit a custom list filter."""

        saved_filter = items_factories.SavedFilterFactory.create(
            user=self.user,
            desk=self.desk,
            type=SavedFilter.TYPE_LIST,
            filter='page=1&page_size=15&total_pages=1&total_entries=1&project=1&start=2014-01-01&end=2014-01-31'
        )

        # Test GET.
        url = reverse('ui_saved_filter', kwargs={'filter_pk': saved_filter.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST. Edit the saved custom list.
        post_data = {
            'title': 'New custom list title',
            'query': saved_filter.query,
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)

        # Refresh the cached saved_filter instance.
        saved_filter = SavedFilter.objects.get(pk=saved_filter.pk)

        self.assertEqual(saved_filter.title, post_data['title'])
        self.assertEqual(saved_filter.type, SavedFilter.TYPE_LIST)

    def test_delete_custom_list(self):
        """Delete a custom list filter."""

        saved_filter = items_factories.SavedFilterFactory.create(
            user=self.user,
            desk=self.desk,
            type=SavedFilter.TYPE_LIST,
            filter='page=1&page_size=15&total_pages=1&total_entries=1&project=1&start=2014-01-01&end=2014-01-31'
        )

        url = reverse('ui_saved_filter_delete', kwargs={'filter_pk': saved_filter.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_items_list'))

        self.assertEqual(0, SavedFilter.objects.filter(pk__in=[saved_filter.pk]).count())

    @skip("SharedFilter has been moved to an API")
    def test_share_custom_list_with_desk(self):
        """Share a custom list at the desk level."""

        # Create a saved filter for the current logged user.
        saved_filter = items_factories.SavedFilterFactory.create(
            user=self.user,
            desk=self.desk,
            type=SavedFilter.TYPE_LIST,
            filter='page=1&page_size=15&total_pages=1&total_entries=1&project=1&start=2014-01-01&end=2014-01-31'
        )

        url = reverse('ui_saved_filter', kwargs={'filter_pk': saved_filter.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST. Share the list filter at the desk level.
        post_data = {
            'title': saved_filter.title,
            'query': saved_filter.query,
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)

        # Refresh the cached saved_filter instance.
        saved_filter = SavedFilter.objects.get(pk=saved_filter.pk)

        # Logout the current user.
        self.client.logout()

        # Create another user on the same desk and on the same organization.
        other_user = pilot_users_factories.AdminFactory.create(password='password')
        self.organization.users.add(other_user)
        self.desk.users.add(other_user)

        # Log the other user in.
        self.client.login(email=other_user.email, password='password')

        # Test GET. The other user should be able to access the desk shared list.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @skip("SharedFilter has been moved to an API")
    def test_share_custom_list_with_external_contact(self):
        """Share a custom list with an external contact (an anonymous user)."""

        # Create 1 project related to the current desk.
        project = projects_factories.ProjectFactory.create(desk=self.desk)

        # Create 5 items related to the project just created.
        items = items_factories.ConfirmedItemFactory.create_batch(size=5, desk=self.desk, project=project)

        # Get the min and max `publication_dt` as start and end.
        start = Task.objects.aggregate(Min('deadline')).values()[0]
        end = Task.objects.aggregate(Max('deadline')).values()[0]

        # Create a saved filter for the current logged user.
        saved_filter = items_factories.SavedFilterFactory.create(
            user=self.user,
            desk=self.desk,
            type=SavedFilter.TYPE_LIST,
            filter='start={0}&end={1}&project={2}'.format(
                start.strftime('%Y-%m-%d'),
                end.strftime('%Y-%m-%d'),
                project.pk
            )
        )

        # GET the custom saved filter.
        url = reverse('ui_saved_filter', kwargs={'filter_pk': saved_filter.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Share the custom list.
        post_data = {
            'email': 'BOB@BOB.COM',
            'password': 'p4ssw0rd',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)

        # Fetch the just created PublicSharedFilter object.
        shared_filter = PublicSharedFilter.objects.get(saved_filter=saved_filter)
        # Ensure that the email is in lower case (EmailLowerCaseField should be used in the Form).
        self.assertEqual(shared_filter.email, post_data['email'].lower())
        url = reverse('ui_shared_filter', kwargs={
            'shared_filter_pk': shared_filter.pk, 'token': shared_filter.token, })

        # An email must have been sent to share the list.
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(shared_filter.email, mail.outbox[0].to)
        self.assertIn(shared_filter.token, mail.outbox[0].body)
        self.assertIn(shared_filter.password, mail.outbox[0].body)
        self.assertIn(url, mail.outbox[0].body)

        DESK_WITHOUT_LANG_ENABLED = 0
        DESK_WITH_LANG_ENABLED = 1

        for desk_to_test in (DESK_WITHOUT_LANG_ENABLED, DESK_WITH_LANG_ENABLED):
            # Logout the current user.
            self.client.logout()

            if desk_to_test == DESK_WITH_LANG_ENABLED:  # Setting language fields for desk and items
                desk = Desk.objects.get(pk=self.desk.pk)
                desk.item_languages_enabled = True
                desk.allowed_languages = ['fr_FR', 'en_US']
                desk.save()
                for item in items:
                    item.language = 'fr_FR'
                    item.save()

            # Try to access the shared list as an anonymous user.
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Should redirect to the password form.

            # Access the password form.
            password_url = reverse('ui_shared_filter_password_required', kwargs={
                'shared_filter_pk': shared_filter.pk, 'token': shared_filter.token, })
            response = self.client.get(password_url)
            self.assertEqual(response.status_code, 200)

            # Fill in the password form.
            post_data = {
                'password': 'p4ssw0rd',
            }
            response = self.client.post(password_url, data=post_data, follow=True)
            self.assertEqual(response.status_code, 200)  # 200 => because follow=True.

            # The shared list should be displayed.
            self.assertContains(response, 'sharedId={0}&sharedToken={1}'.format(
                shared_filter.pk, shared_filter.token))

            # Check for a flag indicating to display language or not
            self.assertContains(response, '<th ng-if="{0}">Langue</th>'.format(['false', 'true'][desk_to_test]))

            api_url = reverse(
                'api_shared_items_list',
                kwargs={
                    'shared_filter_pk': shared_filter.pk,
                    'token': shared_filter.token
                }
            )

            # Checking datagrid api
            response = self.client.get(api_url)
            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content)
            self.assertEqual(5, content['count'])

            if desk_to_test == DESK_WITH_LANG_ENABLED:
                self.assertIn('language', content['objects'][0])
                self.assertEqual(content['objects'][0]['language'], 'Français')
            else:
                self.assertIn('language', content['objects'][0])
                self.assertIsNone(content['objects'][0]['language'])

            # Ensure that the public details view of an item is accessible.
            # Get shared items.
            item_filter = items_filters.ItemFilter(QueryDict(saved_filter.query), Item.objects.all())
            # Select 1 item.
            item = item_filter.queryset[0]
            # GET.
            public_url = reverse('ui_shared_item_details', kwargs={
                'item_pk': item.pk,
                'shared_filter_pk': shared_filter.pk,
                'token': shared_filter.token,
            })
            self.client.session[settings.SESSION_SHARED_FILTER_TOKEN] = shared_filter.token
            response = self.client.get(public_url)
            self.assertEqual(response.status_code, 200)

            del self.client.session[settings.SESSION_SHARED_FILTER_TOKEN]


class CustomCalendarUiTest(PilotAdminUserMixin, TestCase):
    @skip("SharedFilter has been moved to an API")
    def test_save_custom_calendar(self):
        """Save a custom calendar from the main calendar view."""
        url = reverse('ui_main_calendar')
        post_data = {
            'title': 'Custom calendar',
            'query': 'start=2013-09-29&end=2013-11-10&project=2',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)

        saved_filter = SavedFilter.objects.get(title=post_data['title'])

        self.assertEqual(saved_filter.title, post_data['title'])
        self.assertEqual(saved_filter.query, post_data['query'])
        self.assertEqual(saved_filter.type, SavedFilter.TYPE_CALENDAR)

        self.assertRedirects(response, reverse('ui_saved_filter', kwargs={'filter_pk': saved_filter.pk}))

    def test_edit_custom_calendar(self):
        """Display and edit a custom calendar."""

        saved_filter = items_factories.SavedFilterFactory.create(
            user=self.user,
            desk=self.desk,
            type=SavedFilter.TYPE_CALENDAR,
            filter='start=2013-09-29&end=2013-11-10&project=2'
        )

        # Test GET.
        url = reverse('ui_saved_filter', kwargs={'filter_pk': saved_filter.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST. Edit the saved custom calendar.
        post_data = {
            'title': 'New calendar title',
            'query': 'start=2014-12-12&end=2014-12-22&project=2',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)

        # Refresh the cached saved_filter instance.
        saved_filter = SavedFilter.objects.get(pk=saved_filter.pk)

        self.assertRedirects(response, reverse('ui_saved_filter', kwargs={'filter_pk': saved_filter.pk}))
        response = self.client.get(url)

    def test_delete_custom_calendar(self):
        """Test deletion of a saved filter."""

        saved_filter = items_factories.SavedFilterFactory.create(
            user=self.user,
            desk=self.desk,
            type=SavedFilter.TYPE_CALENDAR,
            filter='start=2013-09-29&end=2013-11-10&project=2'
        )

        url = reverse('ui_saved_filter_delete', kwargs={'filter_pk': saved_filter.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_main_calendar'))

        self.assertEqual(0, SavedFilter.objects.filter(pk__in=[saved_filter.pk]).count())

    @skip("SharedFilter has been moved to an API")
    def test_share_custom_calendar_with_desk(self):
        """Share a custom calendar at the desk level."""

        # Create a saved filter for the current logged user.
        saved_filter = items_factories.SavedFilterFactory.create(
            user=self.user,
            desk=self.desk,
            type=SavedFilter.TYPE_CALENDAR
        )

        url = reverse('ui_saved_filter', kwargs={'filter_pk': saved_filter.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST. Share the calendar filter at the desk level.
        post_data = {
            'title': saved_filter.title,
            'query': saved_filter.query,
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)

        # Refresh the cached saved_filter instance.
        saved_filter = SavedFilter.objects.get(pk=saved_filter.pk)

        # Logout the current user.
        self.client.logout()

        # Create another user on the same desk and on the same organization.
        other_user = pilot_users_factories.AdminFactory.create(password='password')
        self.organization.users.add(other_user)
        self.desk.users.add(other_user)

        # Log the other user in.
        self.client.login(email=other_user.email, password='password')

        # Test GET. The other user should be able to access the desk shared calendar.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @skip("SharedFilter has been moved to an API")
    def test_share_custom_calendar_with_external_contact(self):
        """Share a custom calendar with an external contact (an anonymous user)."""

        # Create 1 project related to the current desk.
        project = projects_factories.ProjectFactory.create(desk=self.desk)

        # Create 5 items related to the project just created.
        items = items_factories.ConfirmedItemFactory.create_batch(size=5, desk=self.desk, project=project)

        # Get the min and max `publication_dt` as start and end.
        start = Task.objects.aggregate(Min('deadline')).values()[0]
        end = Task.objects.aggregate(Max('deadline')).values()[0]

        # Create a saved filter for the current logged user.
        saved_filter = items_factories.SavedFilterFactory.create(
            user=self.user,
            desk=self.desk,
            type=SavedFilter.TYPE_CALENDAR,
            filter='start={0}&end={1}&project={2}'.format(
                start.strftime('%Y-%m-%d'),
                end.strftime('%Y-%m-%d'),
                project.pk
            )
        )

        # GET the custom saved filter.
        url = reverse('ui_saved_filter', kwargs={'filter_pk': saved_filter.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Share the custom calendar.
        post_data = {
            'email': 'CHIEF@CHIEF.COM',
            'password': 'secret',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)

        # Fetch the just created PublicSharedFilter object.
        shared_filter = PublicSharedFilter.objects.get(saved_filter=saved_filter)

        # Ensure that the email is in lower case (EmailLowerCaseField should be used in the Form).
        self.assertEqual(shared_filter.email, post_data['email'].lower())
        url = reverse('ui_shared_filter', kwargs={
            'shared_filter_pk': shared_filter.pk, 'token': shared_filter.token, })

        # An email must have been sent to share the calendar.
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(shared_filter.email, mail.outbox[0].to)
        self.assertIn(shared_filter.token, mail.outbox[0].body)
        self.assertIn(shared_filter.password, mail.outbox[0].body)
        self.assertIn(url, mail.outbox[0].body)

        DESK_WITHOUT_LANG_ENABLED = 0
        DESK_WITH_LANG_ENABLED = 1

        for desk_to_test in (DESK_WITHOUT_LANG_ENABLED, DESK_WITH_LANG_ENABLED):
            # Logout the current user.
            self.client.logout()
            if desk_to_test == DESK_WITH_LANG_ENABLED:  # Setting language fields for desk and items
                desk = Desk.objects.get(pk=self.desk.pk)
                desk.item_languages_enabled = True
                desk.allowed_languages = ['fr_FR', 'en_US']
                desk.save()
                for item in items:
                    item.language = 'fr_FR'
                    item.save()

            # Logout the current user.
            self.client.logout()

            # Try to access the shared calendar as an anonymous user.
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Should redirect to the password form.

            # Access the password form.
            password_url = reverse(
                'ui_shared_filter_password_required',
                kwargs={'shared_filter_pk': shared_filter.pk, 'token': shared_filter.token, }
            )
            response = self.client.get(password_url)
            self.assertEqual(response.status_code, 200)

            # Fill in the password form.
            post_data = {
                'password': 'secret',
            }
            response = self.client.post(password_url, data=post_data, follow=True)
            self.assertEqual(response.status_code, 200)  # 200 => because follow=True.

            api_url = reverse(
                'api-items-shared-calendar/(?P<shared-filter-pk>\d+)/(?P<token>\w+)',
                kwargs={
                    'shared_filter_pk': shared_filter.pk,
                    'token': shared_filter.token
                }
            )
            # Checking calendar api
            url_filter = shared_filter.saved_filter.query
            response = self.client.get('{0}?{1}'.format(api_url, url_filter))
            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content)
            self.assertEqual(5, len(content))

            if desk_to_test == DESK_WITH_LANG_ENABLED:
                self.assertIn('language', content[0])
                self.assertEqual(content[0]['language'], 'Français')
            else:
                self.assertIn('language', content[0])
                self.assertIsNone(content[0]['language'])

            # Ensure that the public details view of an item is accessible.
            # Get shared items.
            item_filter = items_filters.ItemFilter(QueryDict(saved_filter.query), Item.objects.all())
            # Select 1 item.
            item = item_filter.queryset.earliest('created_at')
            # GET.
            public_url = reverse('ui_shared_item_details', kwargs={
                'item_pk': item.pk,
                'shared_filter_pk': shared_filter.pk,
                'token': shared_filter.token,
            })
            self.client.session[settings.SESSION_SHARED_FILTER_TOKEN] = shared_filter.token
            response = self.client.get(public_url)
            self.assertEqual(response.status_code, 200)
            del self.client.session[settings.SESSION_SHARED_FILTER_TOKEN]

    def test_sharing_infos_display(self):
        """Test that the sharing infos of a shared custom calendar are displayed."""

        saved_filter = items_factories.SavedFilterFactory.create(
            user=self.user,
            desk=self.desk,
            type=SavedFilter.TYPE_CALENDAR
        )
        shared_filters = items_factories.PublicSharedFilterFactory.create_batch(
            size=3, saved_filter=saved_filter)

        url = reverse('ui_saved_filter', kwargs={'filter_pk': saved_filter.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        for shared_filter in shared_filters:
            self.assertContains(response, shared_filter.email)
            self.assertContains(response, shared_filter.get_absolute_url())

    def test_delete_shared_calendar(self):
        """Test deletion of a shared custom calendar."""

        saved_filter = items_factories.SavedFilterFactory.create(
            user=self.user,
            desk=self.desk,
            type=SavedFilter.TYPE_CALENDAR
        )
        shared_filter = items_factories.PublicSharedFilterFactory.create(saved_filter=saved_filter)

        url = reverse('ui_shared_filter_delete', kwargs={'filter_pk': saved_filter.pk, 'shared_pk': shared_filter.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(PublicSharedFilter.objects.filter(pk=shared_filter.pk).exists())

        # Test POST.
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_saved_filter', kwargs={'filter_pk': saved_filter.pk}))

        with self.assertRaises(PublicSharedFilter.DoesNotExist):
            PublicSharedFilter.objects.get(pk=shared_filter.pk)

class CustomListItemsSeleniumTest(SeleniumTest):
    NB_STANDARD_ITEM = 20
    NB_TWEET_ITEM = 50
    PAGINATION_SIZE = 15

    def setUp(self):
        super(CustomListItemsSeleniumTest, self).setUp()
        self.login_user()

        # Create a bunch of standard items
        items_factories.ConfirmedItemFactory.create_batch(
            size=self.NB_STANDARD_ITEM,
            desk=self.desk
        )

        # Create a bunch of tweet items
        items_factories.ConfirmedItemTweetFactory.create_batch(
            size=self.NB_TWEET_ITEM,
            desk=self.desk
        )

        # Create a custom item list on tweet items
        self.saved_filter = items_factories.SavedFilterFactory.create(
            user=self.user,
            desk=self.desk,
            type=SavedFilter.TYPE_LIST,
            filter='item_type={}'.format(initial_item_types.TWITTER_TYPE)
        )

    def test_extended_list_pagination(self):
        url = reverse('ui_saved_filter', kwargs={'filter_pk': self.saved_filter.pk})
        self.browser.get('%s%s' % (self.live_server_url, url))

        def get_pagination_buttons():
            return self.browser.find_elements_by_css_selector("#tab-listextended ul.pagination li a")

        # Go to the extended list
        self.browser.find_element_by_css_selector(".nav-tabs  li:nth-child(2) a").click()

        extended_list = self.browser.find_element_by_css_selector("#tab-listextended")

        # Wait for the items to appear
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "pilot-extended-items-list > div"))
        )

        # There should be 15 items displayed, for the first page
        items = extended_list.find_elements_by_css_selector("pilot-extended-items-list > div")
        self.assertEqual(len(items), self.PAGINATION_SIZE)

        # There should be 4 pages of items
        nb_pages = (self.NB_TWEET_ITEM / self.PAGINATION_SIZE) + 1

        # There should be first / previous / next / last
        # And 4 pages of items
        pagination_buttons = get_pagination_buttons()
        self.assertEqual(len(pagination_buttons), 4 + nb_pages)

        # First Page
        self.assertEqual(pagination_buttons[0].text, "←")
        # The parent <li> should be disabled because we're on the first page
        self.assertIn('disabled', pagination_buttons[0].find_element_by_xpath('..').get_attribute("class"))

        # Previous Page
        self.assertEqual(pagination_buttons[1].text, "«")
        # The parent <li> should be disabled because we're on the first page
        self.assertIn('disabled', pagination_buttons[1].find_element_by_xpath('..').get_attribute("class"))

        # Assert the 4 buttons for each page are displayed
        for i in range(1, nb_pages + 1):
            self.assertEqual(pagination_buttons[i + 1].text, str(i))

        # Next Page
        self.assertEqual(pagination_buttons[-2].text, "»")

        # Last Page
        self.assertEqual(pagination_buttons[-1].text, "→")

        # Current page (n°1) should be active
        self.assertIn('active', pagination_buttons[2].find_element_by_xpath('..').get_attribute("class"))

        # Scroll to see the pagination buttons
        self.browser.execute_script("arguments[0].scrollIntoView(true);", pagination_buttons[0])

        # Go to the next page (n°2)
        pagination_buttons[-2].click()

        # Wait for the items to appear
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "pilot-extended-items-list > div"))
        )

        # Refresh the button list
        pagination_buttons = get_pagination_buttons()

        # First and Previous buttons are now enabled
        self.assertNotIn('disabled', pagination_buttons[0].find_element_by_xpath('..').get_attribute("class"))
        self.assertNotIn('disabled', pagination_buttons[1].find_element_by_xpath('..').get_attribute("class"))

        # Current page (n°2) should be active
        self.assertIn('active', pagination_buttons[3].find_element_by_xpath('..').get_attribute("class"))

        # We still have 15 items in the list on the second page
        items = extended_list.find_elements_by_css_selector("pilot-extended-items-list > div")
        self.assertEqual(len(items), self.PAGINATION_SIZE)

        # Scroll to see the pagination buttons
        self.browser.execute_script("arguments[0].scrollIntoView(true);", pagination_buttons[0])

        # Back to the first page (n°1)
        pagination_buttons[0].click()

        # Wait for the items to appear
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "pilot-extended-items-list > div"))
        )

        # Refresh the button list
        pagination_buttons = get_pagination_buttons()
        # Current page (n°1) should be active
        self.assertIn('active', pagination_buttons[2].find_element_by_xpath('..').get_attribute("class"))

        # Scroll to see the pagination buttons
        self.browser.execute_script("arguments[0].scrollIntoView(true);", pagination_buttons[0])

        # Go to the last page (n°4)
        pagination_buttons[-1].click()

        # Wait for the items to appear
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "pilot-extended-items-list > div"))
        )

        # Refresh the button list
        pagination_buttons = get_pagination_buttons()
        # Next and Last buttons are now disabled
        self.assertIn('disabled', pagination_buttons[-2].find_element_by_xpath('..').get_attribute("class"))
        self.assertIn('disabled', pagination_buttons[-1].find_element_by_xpath('..').get_attribute("class"))

        # We're on the last page, which should have only 5 items
        items = extended_list.find_elements_by_css_selector("pilot-extended-items-list > div")
        self.assertEqual(len(items), self.NB_TWEET_ITEM % self.PAGINATION_SIZE)

        # Current page (n°4) should be active
        self.assertIn('active', pagination_buttons[5].find_element_by_xpath('..').get_attribute("class"))

        # Scroll to see the pagination buttons
        self.browser.execute_script("arguments[0].scrollIntoView(true);", pagination_buttons[0])

        # Back to the previous page (n°3)
        pagination_buttons[1].click()

        # Wait for the items to appear
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "pilot-extended-items-list > div"))
        )

        # Refresh the button list
        pagination_buttons = get_pagination_buttons()
        # Current page (n°3) should be active
        self.assertIn('active', pagination_buttons[4].find_element_by_xpath('..').get_attribute("class"))

        # Finally, test direct each page accessor
        for i in range(nb_pages):
            # Scroll to see the pagination buttons
            self.browser.execute_script("arguments[0].scrollIntoView(true);", pagination_buttons[0])

            pagination_buttons[i + 2].click()
            # Wait for the items to appear
            WebDriverWait(self.browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "pilot-extended-items-list > div"))
            )
            # Current page should be active
            self.assertIn('active', pagination_buttons[i + 2].find_element_by_xpath('..').get_attribute("class"))

class CustomCalendarLockedItemUiTest(SeleniumTest):

    def setUp(self):
        super(CustomCalendarLockedItemUiTest, self).setUp()
        self.login_user()

    def test_share_custom_calendar_with_external_contact_with_items_locked(self):
        """Share a custom, *items locked*, calendar with an external contact (an anonymous user)."""

        # Create 1 project related to the current desk.
        project = projects_factories.ProjectFactory.create(desk=self.desk)

        # Create 5 items related to the project just created.
        # For unknown reason the tests, while run with others, set publication dates to far, out of scope of
        # 'this month' calendar, thus tests were failing.
        # We group all item on one day today), this is enough for what we have to test here.
        items_factories.ConfirmedItemFactory.create_batch(size=5,
                                                          desk=self.desk,
                                                          publication_dt=timezone.now(),
                                                          project=project)

        # Get the min and max `publication_dt` as start and end.
        start = Task.objects.aggregate(Min('deadline')).values()[0]
        end = Task.objects.aggregate(Max('deadline')).values()[0]

        # Create a saved filter for the current logged user.
        saved_filter = items_factories.SavedFilterFactory.create(
            user=self.user,
            desk=self.desk,
            type=SavedFilter.TYPE_CALENDAR,
            filter='start={0}&end={1}&project={2}'.format(
                start.strftime('%Y-%m-%d'),
                end.strftime('%Y-%m-%d'),
                project.pk
            )
        )
        #
        # # GET the custom saved filter.
        url = reverse('ui_saved_filter', kwargs={'filter_pk': saved_filter.pk})
        self.browser.get('%s%s' % (self.live_server_url, url))

        # Open modal to share the filter and fill in with locking items
        self.browser.find_element_by_css_selector('#launch-share-form-modal').click()
        time.sleep(2)

        input_email_contact = self.browser.find_element_by_css_selector('#id_email')
        input_email_contact.send_keys("testcontact@test.com")
        self.browser.find_element_by_css_selector('#id_items_locked').click()

        SUBMIT_BUTTON_XPATH = "//div[@class='form-group'][4]/div[@class='col-lg-offset-2 col-lg-10']//button[@class='btn btn-primary']"
        self.browser.find_element_by_xpath(SUBMIT_BUTTON_XPATH).click()

        # Get the freshly created share link and open the shared calendar
        SHARE_LINKS_TAB = "//ul[@class='nav nav-tabs']/li[2]/a/span[@class='lead']"
        SHARE_LINK = "//table[@class='table table-striped']/tbody/tr/td[4]/a"

        self.browser.find_element_by_xpath(SHARE_LINKS_TAB).click()
        get_share_link = self.browser.find_element_by_xpath(SHARE_LINK)

        # Logout client to mimic an external contact
        self.browser.delete_all_cookies()

        # Got o shared calendar
        share_url_parse = urlparse.urlparse(get_share_link.text)
        self.browser.get('%s%s' % (self.live_server_url, share_url_parse.path))

        # get current url
        before_url = self.browser.current_url
        # click on item
        self.browser.find_elements_by_css_selector('.fc-title')[0].click()
        after_url = self.browser.current_url

        self.assertEqual(before_url, after_url)

    def test_share_custom_calendar_with_external_contact_without_items_locked(self):
        """Share a custom, *items NOT BEING locked*, calendar with an external contact (an anonymous user)."""

        # Create 1 project related to the current desk.
        project = projects_factories.ProjectFactory.create(desk=self.desk)

        # Create 5 items related to the project just created.
        # For unknown reason the tests, while run with others, set publication dates to far, out of scope of
        # 'this month' calendar, thus tests were failing.
        # We group all item on one day today), this is enough for what we have to test here.
        items_factories.ConfirmedItemFactory.create_batch(size=5,
                                                          desk=self.desk,
                                                          publication_dt=timezone.now(),
                                                          project=project)

        # Get the min and max `publication_dt` as start and end.
        start = Task.objects.aggregate(Min('deadline')).values()[0]
        end = Task.objects.aggregate(Max('deadline')).values()[0]
        #
        # # Create a saved filter for the current logged user.
        saved_filter = items_factories.SavedFilterFactory.create(
            user=self.user,
            desk=self.desk,
            type=SavedFilter.TYPE_CALENDAR,
            filter='start={0}&end={1}&project={2}'.format(
                start.strftime('%Y-%m-%d'),
                end.strftime('%Y-%m-%d'),
                project.pk
            )
        )
        #
        # # GET the custom saved filter.
        url = reverse('ui_saved_filter', kwargs={'filter_pk': saved_filter.pk})
        self.browser.get('%s%s' % (self.live_server_url, url))

        # Open modal to share the filter and fill in with locking items
        self.browser.find_element_by_css_selector('#launch-share-form-modal').click()
        time.sleep(2)

        input_email_contact = self.browser.find_element_by_css_selector('#id_email')
        input_email_contact.send_keys("testcontact@test.com")

        SUBMIT_BUTTON_XPATH = "//div[@class='form-group'][4]/div[@class='col-lg-offset-2 col-lg-10']//button[@class='btn btn-primary']"
        self.browser.find_element_by_xpath(SUBMIT_BUTTON_XPATH).click()

        # Get the freshly created share link and open the shared calendar
        SHARE_LINKS_TAB = "//ul[@class='nav nav-tabs']/li[2]/a/span[@class='lead']"
        SHARE_LINK = "//table[@class='table table-striped']/tbody/tr/td[4]/a"

        self.browser.find_element_by_xpath(SHARE_LINKS_TAB).click()
        get_share_link = self.browser.find_element_by_xpath(SHARE_LINK)

        # Logout client to mimic an external contact
        self.browser.delete_all_cookies()

        # Got o shared calendar
        share_url_parse = urlparse.urlparse(get_share_link.text)
        self.browser.get('%s%s' % (self.live_server_url, share_url_parse.path))

        # get current url
        before_url = self.browser.current_url
        # click on item
        self.browser.find_elements_by_css_selector('.fc-title')[0].click()
        after_url = self.browser.current_url

        self.assertNotEqual(before_url, after_url)
