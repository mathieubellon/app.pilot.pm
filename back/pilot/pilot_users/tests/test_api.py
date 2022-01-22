import json

from django.urls import reverse

from rest_framework.test import APITestCase

from pilot.pilot_users.tests import factories as pilot_users_factories
from pilot.utils.test import PilotAdminUserMixin
from pilot.desks.tests import factories as desks_factories


class PilotUserApiTest(PilotAdminUserMixin, APITestCase):

    PILOT_USER_API_FIELDS = ('id', 'username', 'avatar')

    def assert_api_pilot_user_fields(self, user):
        for field_name in self.PILOT_USER_API_FIELDS:
            self.assertIn(field_name, user)

    def test_list(self):
        users = pilot_users_factories.PilotUserFactory.create_batch(10)

        self.organization.users.add(*users)
        self.desk.users.add(*users)

        # Adding users from another desk and same organization
        other_desk = desks_factories.DeskFactory(organization=self.organization)
        other_desk_users = pilot_users_factories.PilotUserFactory.create_batch(10)
        other_desk.users.add(*other_desk_users)
        self.organization.users.add(*other_desk_users)

        response = self.content('api-users-list')
        self.assert_api_pilot_user_fields(response[0])

        # Ensuring there are only users from the same desk
        self.assertEqual(len(response), len(users + [self.user]))

    def test_filter_by_name(self):
        for name in ["User genial", "User genial2"]:
            user = pilot_users_factories.PilotUserFactory.create(username=name)
            self.organization.users.add(user)
            self.desk.users.add(user)

        users = self.content('api-users-list', filter = {'username': "genia"})
        self.assertEqual(2, len(users))
        api_user = users[0]
        self.assert_api_pilot_user_fields(api_user)

        users = self.content('api-users-list', filter = {'username': "génia"})
        self.assertEqual(0, len(users))

    def test_me(self):
        """
        Test that we can retrieve the connected user through the API
        """
        json_user = self.content('api-users-me')

        self.assert_api_pilot_user_fields(json_user)
        self.assertEqual(self.user.id, json_user['id'])
        self.assertEqual(self.user.username, json_user['username'])
        self.assertEqual("%s" % self.user.get_avatar_url(), json_user['avatar'])

    def content(self, url_id, filter=None):
        response = self.client.get(reverse(url_id), data=filter)
        self.assertEqual(response.status_code, 200)
        return json.loads(response.content)
