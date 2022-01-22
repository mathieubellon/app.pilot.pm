import datetime
import json

from django.urls import reverse
from django.db.models import Min, Max
from django.utils.timezone import utc
from rest_framework.test import APITestCase

from pilot.pilot_users.tests import factories as pilot_users_factories
from pilot.projects.models import Project
from pilot.projects.tests import factories as projects_factories
from pilot.channels.tests import factories as channels_factories
from pilot.desks.tests import factories as desks_factories
from pilot.items.tests import factories as items_factories
from pilot.utils import states
from pilot.utils.test import PilotAdminUserMixin, PilotRestrictedEditorUserMixin


class projectsOrderApiTest(PilotAdminUserMixin, APITestCase):

    def get_names(self, filter_param):
        url = reverse('api-projects-list')
        filter = {'order_by': filter_param}
        response = self.client.get(url, data=filter, format='json')
        content = json.loads(response.content)
        return map(lambda obj: obj['name'], content['objects'])

    def test_order_by_end(self):
        for day in range(5):
            # Set a constant date far away from DST-switches
            now = datetime.datetime(2018,1,1,12,0,0,tzinfo=utc)
            projects_factories.ProjectFactory.create(
                name='{}'.format(day),
                desk=self.desk,
                start=now + datetime.timedelta(days=day)
            )

        for order_param in ['id', 'end', 'start', 'name', 'created_at', 'updated_at']:
            self.assertEqual([u'0', u'1', u'2', u'3', u'4'], self.get_names('{}'.format(order_param)))
            self.assertEqual([u'4', u'3', u'2', u'1', u'0'], self.get_names('-{}'.format(order_param)))

    def test_priority(self):
        for priority in [Project.HIGH, Project.AVERAGE, Project.NORMAL]:
            projects_factories.ProjectFactory.create(
                name=priority,
                desk=self.desk,
                priority= priority
            )

        self.assertEqual([u'1_high', u'2_average', u'3_normal'], self.get_names('priority'))
        self.assertEqual([u'3_normal', u'2_average', u'1_high'], self.get_names('-priority'))


class projectListApiTest(PilotAdminUserMixin, APITestCase):
    """Test the API for projects"""

    PROJECT_API_READ_ONLY_FIELDS = ('id', 'url', 'name', 'start', 'end', 'owners', 'state', 'state_label', 'channels',
                                     'progress', 'priority')
    PROJECT_API_UPDATABLE_FIELDS = ()
    PROJECT_API_FIELDS = PROJECT_API_READ_ONLY_FIELDS + PROJECT_API_UPDATABLE_FIELDS
    URL = 'api-projects-list'

    def setUp(self):
        super(projectListApiTest, self).setUp()

        self.url = reverse(self.URL)

        self.restricted_user = pilot_users_factories.RestrictedEditorFactory.create(password='password')
        self.organization.users.add(self.restricted_user)
        self.desk.users.add(self.restricted_user)

        self.channels = [channels_factories.ChannelFactory.create(desk=self.desk),
                         channels_factories.ChannelFactory.create(desk=self.desk)]

        self.projects = []
        self.nb_projects = 0

        for [size, channel_pos, owners, state] in [
                [3, [0], None, states.STATE_ACTIVE],
                [4, [1], None, states.STATE_ACTIVE],
                [5, [0], [self.restricted_user], states.STATE_ACTIVE],
                [6, [1], [self.restricted_user], states.STATE_ACTIVE],
                [7, [0, 1], [self.user, self.restricted_user], states.STATE_ACTIVE],
                [8, [], None, states.STATE_CLOSED]
                ]:
            channels = [self.channels[id] for id in channel_pos]
            self.projects += [projects_factories.ProjectFactory.create_batch(
                size=size,
                desk=self.desk,
                channels=channels,
                owners=owners,
                state=state)]
            self.nb_projects += size

        # Rejected projects should not be sent by the API
        projects_factories.ProjectFactory.create_batch(size=5, state=states.STATE_REJECTED)
        # projects on another desk should not be sent by the API
        projects_factories.ProjectFactory.create_batch(size=5)

    def assert_common_api_item_fields(self, item):
        for field_name in self.PROJECT_API_FIELDS:
            self.assertIn(field_name, item)

    def test_list(self):
        content = self.content()

        self.assertEqual(self.nb_projects, content['count'])
        self.assertEqual((self.nb_projects / 10) + 1, content['num_pages'])

        self.assert_common_api_item_fields(content['objects'][0])

    def test_list_restricted(self):
        self.client.logout()
        self.client.login(email=self.restricted_user.email, password='password')

        content = self.content()

        self.assertEqual(len(self.projects[2]) + len(self.projects[3]) + len(self.projects[4]), content['count'])
        self.assert_common_api_item_fields(content['objects'][0])

    def test_list_filter_by_id(self):
        project = self.projects[0][0]
        # Filter by id
        content = self.content(filter = {'q': project.id})

        # Only one project should be found
        self.assertEqual(1, content['count'])
        # And have the correct id
        api_project = content['objects'][0]
        self.assert_common_api_item_fields(api_project)
        self.assertEqual(api_project['id'], project.id)

    def test_list_filter_by_name(self):
        # Test with special characters
        for name in ["Projet géniale", "Projet géniale", "Projet goniale"]:
            projects_factories.ProjectFactory.create(desk=self.desk, name=name)

        # Filter by name
        content = self.content(filter={'q': "genia"})

        # Both accentuated and unaccentuated should come back
        self.assertEqual(2, content['count'])
        api_project = content['objects'][0]
        self.assert_common_api_item_fields(api_project)

        # Again, but with accentuated search
        content = self.content(filter={'q': "génia"})
        # Both accentuated and unaccentuated should come back
        self.assertEqual(2, content['count'])

    def test_list_filter_by_date(self):
        # Reset projects
        Project.objects.all().delete()

        # Set a constant date far away from DST-switches
        now = datetime.datetime(2018,1,1,12,0,0,tzinfo=utc)

        def date(days):
            return now + datetime.timedelta(days=days)

        def strdate(days):
            return date(days).strftime('%Y-%m-%d')

        def assert_date_filtering(count_expected, startdays=None, enddays=None):
            filter = {}
            if startdays is not None:
                filter['start'] = strdate(startdays)
            if enddays is not None:
                filter['end'] = strdate(enddays)
            content = self.content(filter)
            self.assertEqual(count_expected, content['count'])

        projects_factories.ProjectFactory.create(
            desk=self.desk,
            start=date(days=1),
            end=date(days=5),
        )
        projects_factories.ProjectFactory.create(
            desk=self.desk,
            start=date(days=3),
            end=date(days=7),
        )

        # Test every combination
        assert_date_filtering(2, startdays=5)
        assert_date_filtering(1, startdays=7)
        assert_date_filtering(0, startdays=8)
        assert_date_filtering(2, enddays=4)
        assert_date_filtering(1, enddays=2)
        assert_date_filtering(0, enddays=0)
        assert_date_filtering(2, startdays=0, enddays=8)
        assert_date_filtering(2, startdays=4, enddays=4)
        assert_date_filtering(1, startdays=6, enddays=8)
        assert_date_filtering(0, startdays=-1, enddays=0)
        assert_date_filtering(0, startdays=8, enddays=9)

    def test_list_filter_by_channels(self):
        # Filter by channel
        content = self.content(filter = {'channels': self.channels[0].id})

        # Only projects with corresponding channel should be found
        self.assertEqual(len(self.projects[0]) + len(self.projects[2]) + len(self.projects[4]), content['count'])
        # And have the correct channel
        api_project = content['objects'][0]
        self.assert_common_api_item_fields(api_project)
        if 'channels' in self.PROJECT_API_FIELDS:
            self.assertEqual(api_project['channels'][0]['id'], self.channels[0].id)

    def test_api_projects_list_filter_by_owners(self):
        # Filter by owner
        content = self.content(filter = {'owners': self.restricted_user.id})

        # Only projects with corresponding channel should be found
        self.assertEqual(len(self.projects[2]) + len(self.projects[3]) + len(self.projects[4]), content['count'])
        # And have the correct owner
        api_project = content['objects'][0]
        self.assert_common_api_item_fields(api_project)
        if 'owners' in self.PROJECT_API_FIELDS:
            self.assertIn(self.restricted_user.id, [ owner['id'] for owner in api_project['owners'] ])

    def test_list_filter_by_state(self):
        # Filter by state
        content = self.content(filter = {'state': states.STATE_CLOSED})

        # Only closed projects should be found
        self.assertEqual(len(self.projects[5]), content['count'])
        # And have the correct id
        api_project = content['objects'][0]
        self.assert_common_api_item_fields(api_project)
        if 'state' in self.PROJECT_API_FIELDS:
            self.assertEqual(api_project['state'], states.STATE_CLOSED)

    def content(self, filter=None):
        response = self.client.get(self.url, data=filter, format='json')
        return json.loads(response.content)


class CalendarprojectsApiTest(PilotAdminUserMixin, APITestCase):
    """Test the API for projects fetched via FullCalendar."""

    def test_calendar_projects_list(self):
        """Test the 'api_calendar_projects_list' method used via FullCalendar."""

        url = reverse('api_calendar_projects_list')

        # Create a bunch of projects.
        projects = projects_factories.ProjectFactory.create_batch(size=10, desk=self.desk)
        # Get the min and max `publication_dt` as start and end.
        start = Project.objects.aggregate(Min('start')).values()[0]
        end = Project.objects.aggregate(Max('end')).values()[0]

        # Call 'api_calendar_projects_list' for projects between start and end.
        url_query_string = '{0}?start={1}&end={2}'.format(url, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))

        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(content), len(projects))
        for key in ('id', 'title', 'text', 'start', 'end', 'color', 'url', 'state'):
            self.assertTrue(key in content[0].keys())

        # Call 'api_calendar_projects_list' for projects overlapping start and end.
        url_query_string = '{0}?start={1}&end={2}'.format(
            url, (start + datetime.timedelta(days=3)).strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))

        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(content), len(projects))

        # Call 'api_calendar_projects_list' for projects overlapping start and end.
        url_query_string = '{0}?start={1}&end={2}'.format(
            url, start.strftime('%Y-%m-%d'), (end - datetime.timedelta(days=10)).strftime('%Y-%m-%d'))

        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(content), len(projects))

        # Change start and end values. Search for nonexistent Project.
        start = start - datetime.timedelta(days=31)
        end = start + datetime.timedelta(days=20)
        url_query_string = '{0}?start={1}&end={2}'.format(url, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        response = self.client.get(url_query_string, format='json')
        self.assertEqual(len(json.loads(response.content)), 0)

    def test_calendar_projects_list_perms(self):
        """Test the 'api_calendar_items_list' perms."""

        url = reverse('api_calendar_projects_list')

        # Create another desk for another user.
        other_desk = desks_factories.DeskFactory.create()

        # Create a bunch of projects related to the other desk.
        other_projects = projects_factories.ProjectFactory.create_batch(size=10, desk=other_desk)

        # Get the min and max `publication_dt` as start and end.
        start = Project.objects.aggregate(Min('start')).values()[0]
        end = Project.objects.aggregate(Max('end')).values()[0]

        # The current logged user should have no projects returned by the API.
        url_query_string = '{0}?start={1}&end={2}'.format(url, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        response = self.client.get(url_query_string, format='json')
        self.assertEqual(len(json.loads(response.content)), 0)

        self.client.logout()

        # Log the other user in.
        self.client.login(email=other_desk.created_by.email, password='password')

        # All projects of the other user should be returned by the API.
        url_query_string = '{0}?start={1}&end={2}'.format(url, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        response = self.client.get(url_query_string, format='json')
        self.assertEqual(len(json.loads(response.content)), len(other_projects))

        # Access should be denied to non logged users
        self.client.logout()

        response = self.client.get(url_query_string, format='json')
        self.assertEqual(response.status_code, 403)

    def test_calendar_shared_projects_list(self):
        """Test the public 'api_calendar_shared_projects_list' method used via FullCalendar."""

        # Create 10 projects related to the current desk.
        projects = projects_factories.ProjectFactory.create_batch(size=10, desk=self.desk)

        # Get the min and max `publication_dt` as start and end.
        start = Project.objects.aggregate(Min('start')).values()[0]
        end = Project.objects.aggregate(Max('end')).values()[0]
        # Create a saved filter for the current logged user.
        saved_filter = items_factories.SavedFilterFactory.create(
            user=self.user,
            desk=self.desk,
            type=SavedFilter.TYPE_CALENDAR,
            filter='start={0}&end={1}'.format(
                start.strftime('%Y-%m-%d'),
                end.strftime('%Y-%m-%d'),
            )
        )

        # Create a shared filter.
        shared_filter = items_factories.PublicSharedFilterFactory.create(saved_filter=saved_filter)

        # Logout the current user.
        self.client.logout()

        url = reverse(
            'api_calendar_shared_projects_list',
            kwargs={'shared_filter_pk': shared_filter.pk, 'token': shared_filter.token, }
        )
        url_query_string = '{0}?{1}'.format(url, saved_filter.query)
        response = self.client.get(url_query_string, format='json')
        json_response = json.loads(response.content)

        # Ensure a public call to the 'api_calendar_shared_items_list' method is possible.
        # Ensure that only items related to project1 are displayed.
        self.assertEqual(len(json_response), len(projects))

        # # Ensure that the response contains public URLs.
        # urls = [i['url'] for i in json_response]
        # for item in Item.objects.filter(project=project1):
        #     public_url = reverse('ui_shared_item_details', kwargs={
        #         'item_pk': item.pk,
        #         'shared_filter_pk': shared_filter.pk,
        #         'token': shared_filter.token,
        #     })
        #     self.assertIn(public_url, urls)

        # No languages if desk international mode is disabled
        # self.assertFalse(self.desk.item_languages_enabled)
        # self.assertFalse('language' in json_response[0])

        # # Enabling international mode
        # desk = Desk.objects.get(pk=self.desk.pk)
        # desk.item_languages_enabled = True
        # desk.allowed_languages = ['fr_FR', 'en_us']
        # desk.save()
        # response = self.client.get(url_query_string, format='json')
        # json_response = json.loads(response.content)
        # self.assertTrue('language' in json_response[0])


class CalendarprojectsApiForRestrictedEditorsTest(PilotRestrictedEditorUserMixin, APITestCase):
    """Test the API for items fetched via FullCalendar for restricted editors."""

    def test_calendar_items_list(self):
        """Test the 'api_calendar_projects_list' method used via FullCalendar for restricted editors."""

        url = reverse('api_calendar_projects_list')

        # Create a bunch of projects.
        projects_factories.ProjectFactory.create_batch(size=7, desk=self.desk)
        projects_created_by_restricted_editor = projects_factories.ProjectFactory.create_batch(
            size=3,
            desk=self.desk,
            created_by=self.restricted_user)

        projects_owned_by_restricted_editor = projects_factories.ProjectFactory.create_batch(
            size=3,
            desk=self.desk)
        for c in projects_owned_by_restricted_editor:
            c.owners.add(self.restricted_user)

        # Get the min and max `publication_dt` as start and end.
        start = Project.objects.aggregate(Min('start')).values()[0]
        end = Project.objects.aggregate(Max('end')).values()[0]

        # Call 'api_calendar_projects_list' for projects between start and end.
        url_query_string = '{0}?start={1}&end={2}'.format(url, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))

        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(
            len(content),
            len(projects_created_by_restricted_editor) + len(projects_owned_by_restricted_editor))
