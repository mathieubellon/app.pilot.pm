import json

from django.urls import reverse
from rest_framework.test import APITestCase

from pilot.pilot_users.tests import factories as pilot_users_factories
from pilot.channels.tests import factories as channels_factories
from pilot.utils import states
from pilot.utils.test import PilotAdminUserMixin


class ChannelsListApiTest(PilotAdminUserMixin, APITestCase):
    """Test the API for projects"""

    CHANNEL_API_READ_ONLY_FIELDS = ('id', 'url', 'name', 'type', 'description', 'state', 'owners')
    CHANNEL_API_UPDATABLE_FIELDS = ()
    CHANNEL_API_FIELDS = CHANNEL_API_READ_ONLY_FIELDS + CHANNEL_API_UPDATABLE_FIELDS
    URL = 'api-channels-list'

    def setUp(self):
        super(ChannelsListApiTest, self).setUp()

        self.url = reverse(self.URL)

        self.restricted_user = pilot_users_factories.RestrictedEditorFactory.create(password='password')
        self.organization.users.add(self.restricted_user)
        self.desk.users.add(self.restricted_user)

        self.channels = []
        self.nb_channels = 0

        self.cms_type = self.desk.channel_types.get(icon=ChannelType.Icon.GLOBE)
        self.print_type = self.desk.channel_types.get(icon=ChannelType.Icon.BOOK)
        self.facebook_type = self.desk.channel_types.get(icon=ChannelType.Icon.FACEBOOK)

        for [size, channel_type, owners, state] in [
                [3, self.cms_type, None, None],
                [4, self.print_type, None, None],
                [5, self.cms_type, [self.restricted_user], None],
                [6, self.print_type, [self.restricted_user], None],
                [7, self.facebook_type, [self.user, self.restricted_user], None],
                [8, self.facebook_type, None, states.STATE_CLOSED]
                ]:
            state = states.STATE_ACTIVE if not state else state
            self.channels += [channels_factories.ChannelFactory.create_batch(
                size=size,
                desk=self.desk,
                type=channel_type,
                owners=owners,
                state=state
            )]
            self.nb_channels += size

        # Channels on another desk should not be sent by the API
        channels_factories.ChannelFactory.create_batch(size=5)

    def assert_common_api_item_fields(self, channel):
        for field_name in self.CHANNEL_API_FIELDS:
            self.assertIn(field_name, channel)

    def test_api_channels_list(self):
        channels = self.get_api_channels()['objects']
        self.assert_common_api_item_fields(channels[0])

    def test_list_restricted(self):
        self.client.logout()
        self.client.login(email=self.restricted_user.email, password='password')

        response = self.get_api_channels()

        self.assertEqual(len(self.channels[2]) + len(self.channels[3]) + len(self.channels[4]), int(response['count']))
        api_channel = response['objects'][0]
        self.assert_common_api_item_fields(api_channel)

    def test_list_filter_by_name(self):
        # Test with special characters
        for name in ["Canal génial", "Canal ginial", "Canal genial"]:
            channels_factories.ChannelFactory.create(desk=self.desk, name=name)

        # Filter by name
        channels = self.get_api_channels(filter={'q': "genia"})['objects']

        # Accentuated and unaccentuated should come back
        self.assertEqual(2, len(channels))
        self.assert_common_api_item_fields(channels[0])

    def test_list_channels_by_type(self):
        # Filter by channel
        channels = self.get_api_channels(filter={'type': self.cms_type.id})['objects']

        # Only channels with corresponding type should be found
        self.assertEqual(len(self.channels[0]) + len(self.channels[2]), len(channels))
        # And have the correct type
        api_channel = channels[0]
        self.assert_common_api_item_fields(api_channel)
        self.assertEqual(api_channel['type'], self.cms_type.name)

    def test_list_filter_by_owners(self):
        # Filter by owner
        response = self.get_api_channels(filter={'owners': self.restricted_user.id})

        # Only projects with corresponding channel should be found
        self.assertEqual(len(self.channels[2]) + len(self.channels[3]) + len(self.channels[4]), int(response['count']))
        # And have the correct owner
        api_channel = response['objects'][0]
        self.assert_common_api_item_fields(api_channel)
        self.assertIn(self.restricted_user.id, [ owner['id'] for owner in api_channel['owners'] ])

    def get_api_channels(self, filter=None):
        response = self.client.get(self.url, data=filter, format='json')
        return json.loads(response.content)
