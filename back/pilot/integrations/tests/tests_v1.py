from unittest import skip

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from django.urls import reverse

from pilot.channels.tests import factories as channels_factories
from pilot.items.tests import factories as items_factories
from pilot.targets.tests import factories as targets_factories
from pilot.utils.test import PilotAdminUserMixin
from pilot.workflow.initial_states import InitialStateNames

@skip('Public API is disabled for now')
class PublicApiApiTest(PilotAdminUserMixin, APITestCase):
    """Test the public API"""

    def setUp(self):
        super(PublicApiApiTest, self).setUp()

        # Create cms channels and related to the current desk.
        self.channeltoken1 = channels_factories.ChannelTokenFactory.create(channel__desk=self.desk)
        self.channeltoken2 = channels_factories.ChannelTokenFactory.create(channel__desk=self.desk)

        # Create channel with a publication_target and related to the current desk.
        self.facebook_channel = channels_factories.FacebookChannelFactory.create(desk=self.desk)

        self.anonymous_client = APIClient()

        # Create a bunch of items related to different channels. We only want to retrieve publishable or published
        # items related to the first channel token

        # Create published and publication ready items (10) for the first cms channel.
        self.number_of_published_items = 5
        self.number_of_publication_ready_items = 7

        target_1 = targets_factories.TargetFactory.create(desk=self.desk)
        target_2 = targets_factories.TargetFactory.create(desk=self.desk)

        self.published_items = items_factories.ItemFactory.create_batch(
            size=self.number_of_published_items,
            desk=self.desk,
            channel=self.channeltoken1.channel,
            state=InitialStateNames.PUBLISHED,
            targets=[target_1, target_2],
        )
        self.publication_ready_items = items_factories.ItemFactory.create_batch(
            size=self.number_of_publication_ready_items,
            desk=self.desk,
            channel=self.channeltoken1.channel,
            state=InitialStateNames.PUBLICATION_READY,
            targets=[target_1, target_2],
        )

        # Create published and publication ready items (10) for the second cms channel.
        self.second_channel_items = items_factories.ItemFactory.create_batch(
            size=5,
            desk=self.desk,
            channel=self.channeltoken2.channel,
            state=InitialStateNames.PUBLICATION_READY,
            targets=[target_1, target_2],
        )

        # Create published or publication ready items for the print channel.
        self.print_channel_items = items_factories.ItemFactory.create_batch(
            size=5,
            desk=self.desk,
            channel=self.facebook_channel,
            state=InitialStateNames.PUBLISHED,
            targets=[target_1, target_2],
        )

        self.items_all = Item.objects.filter(desk=self.desk)

        for item in self.items_all:
            self.assertEqual(item.desk, item.channel.desk)

            for target in item.targets.all():
                self.assertEqual(item.desk, target.desk)

    def test_public_api_items_list(self):
        """Test the 'public_api_item_list'."""

        # good token and appropriate channel
        header = {'HTTP_CHANNELTOKEN': self.channeltoken1.token}  # channel token goes in a custom header

        response = self.anonymous_client.get(reverse('public_api_item_list'), {}, **header)

        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('id' in data[0])
        self.assertTrue('publication_dt' in data[0])
        self.assertTrue('content' in data[0])
        self.assertTrue('author' in data[0])
        self.assertTrue('state' in data[0])
        self.assertTrue('title' in data[0])
        self.assertTrue('url' in data[0])

        # we have created 5 ready to publish items related to this channel token
        self.assertEqual(len(data), self.number_of_publication_ready_items)
        for item in response.data:
            self.assertEqual(item.get('state', None), InitialStateNames.PUBLICATION_READY)

        # checking explicitly ready to publish items
        response = self.anonymous_client.get(reverse('public_api_item_list'),
                                             {'state': InitialStateNames.PUBLICATION_READY}, **header)
        self.assertEqual(len(response.data), self.number_of_publication_ready_items)
        for item in response.data:
            self.assertEqual(item.get('state', None), InitialStateNames.PUBLICATION_READY)

        # checking published items
        response = self.anonymous_client.get(reverse('public_api_item_list'),
                                             {'state': InitialStateNames.PUBLISHED}, **header)
        self.assertEqual(len(response.data), self.number_of_published_items)
        for item in response.data:
            self.assertEqual(item.get('state', None), InitialStateNames.PUBLISHED)

        # checking all items
        response = self.anonymous_client.get(reverse('public_api_item_list'), {'state': 'all'}, **header)
        self.assertEqual(len(response.data), self.number_of_publication_ready_items + self.number_of_published_items)
        for item in response.data:
            self.assertIn(item.get('state', None), (InitialStateNames.PUBLICATION_READY,
                                                    InitialStateNames.PUBLISHED))

        # non existent token
        header = {'HTTP_CHANNELTOKEN': 'nonexistentotken'}

        response = self.anonymous_client.get(reverse('public_api_item_list'), {}, **header)

        data = response.data
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data.get('detail', None), "Pas trouvé.")

    def test_public_api_item_retrieve(self):
        """Test the 'public_api_item_detail' with GET method"""

        # good token and appropriate item pk
        header = {'HTTP_CHANNELTOKEN': self.channeltoken1.token}  # channel token goes in a custom header

        pk = self.publication_ready_items[0].pk

        response = self.anonymous_client.get(reverse('public_api_item_detail', kwargs={'pk': pk}), {}, **header)

        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get('id', None), pk)
        self.assertTrue('publication_dt' in data)
        self.assertTrue('state' in data)
        self.assertTrue('content' in data)
        self.assertTrue('author' in data)
        self.assertTrue('title' in data)
        self.assertTrue('url' in data)

        # token and pk mismatch
        second_channel_item_pk = self.second_channel_items[0].pk
        response = self.anonymous_client.get(reverse('public_api_item_detail',
                                                     kwargs={'pk': second_channel_item_pk}), {}, **header)
        self.assertEqual(response.status_code, 404)

        # non existent token
        header = {'HTTP_CHANNELTOKEN': 'nonexistentotken'}

        response = self.anonymous_client.get(reverse('public_api_item_detail', kwargs={'pk': pk}), {}, **header)
        data = response.data
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data.get('detail', None), "Pas trouvé.")

    def test_public_api_item_patch(self):
        """Test the 'public_api_item_detail' with PATCH method"""

        # good token, good payload and appropriate item pk
        header = {'HTTP_CHANNELTOKEN': self.channeltoken1.token}  # channel token goes in a custom header

        item_to_publish = self.publication_ready_items[0]

        payload = {'op': 'replace', 'state': InitialStateNames.PUBLISHED}
        response = self.anonymous_client.patch(reverse('public_api_item_detail', kwargs={'pk': item_to_publish.pk}),
                                               payload, **header)

        item_to_publish = Item.objects.get(pk=item_to_publish.pk)  # we need to reload it to check update

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(item_to_publish.state.name, InitialStateNames.PUBLISHED)

        # bad state must return an error
        payload = {'op': 'replace', 'state': InitialStateNames.PUBLICATION_READY}
        response = self.anonymous_client.patch(reverse('public_api_item_detail', kwargs={'pk': item_to_publish.pk}),
                                               payload, **header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # bad op must return an error
        payload = {'op': 'foobar', 'state': InitialStateNames.PUBLISHED}
        response = self.anonymous_client.patch(
            reverse('public_api_item_detail', kwargs={'pk': item_to_publish.pk}), payload, **header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # already published item must return an error
        payload = {'op': 'replace', 'state': InitialStateNames.PUBLISHED}

        already_published_item = self.published_items[0]

        response = self.anonymous_client.patch(
            reverse('public_api_item_detail', kwargs={'pk': already_published_item.pk}), payload, **header)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # token and pk mismatch must return an non found error
        second_channel_item_pk = self.second_channel_items[0]
        payload = {'op': 'replace', 'state': InitialStateNames.PUBLISHED}

        response = self.anonymous_client.patch(
            reverse('public_api_item_detail', kwargs={'pk': second_channel_item_pk.pk}),
            payload, **header)
        self.assertEqual(response.status_code, 404)

        # non existent token a non found error
        header = {'HTTP_CHANNELTOKEN': 'nonexistentotken'}

        response = self.anonymous_client.patch(reverse('public_api_item_detail', kwargs={'pk': item_to_publish.pk}),
                                               payload, **header)
        data = response.data
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data.get('detail', None), "Pas trouvé.")

@skip('Public API is disabled for now')
class PublicApiChannelsHierarchyTest(PilotAdminUserMixin, APITestCase):
    """Test the public API with hierarchies of channels"""

    def setUp(self):
        super(PublicApiChannelsHierarchyTest, self).setUp()

        self.anonymous_client = APIClient()

        self.channel = channels_factories.ChannelFactory.create(desk=self.desk)
        self.subchannel = channels_factories.ChannelFactory.create(desk=self.desk,
                                                                   parent=self.channel)

        self.channeltoken = channels_factories.ChannelTokenFactory.create(channel=self.channel)
        self.subchanneltoken = channels_factories.ChannelTokenFactory.create(channel=self.subchannel)

        self.nb_channel_items = 3
        self.channel_items = items_factories.ItemFactory.create_batch(
            size=self.nb_channel_items,
            desk=self.desk,
            channel=self.channel,
            state=InitialStateNames.PUBLICATION_READY
        )
        self.nb_subchannel_items = 3
        self.subchannel_items = items_factories.ItemFactory.create_batch(
            size=self.nb_subchannel_items,
            desk=self.desk,
            channel=self.subchannel,
            state=InitialStateNames.PUBLICATION_READY
        )

    def test_subchannel_items_are_listed_if_token_on_parent(self):
        header = {'HTTP_CHANNELTOKEN': self.channeltoken.token}
        response = self.anonymous_client.get(reverse('public_api_item_list'), {}, **header)

        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), self.nb_subchannel_items + self.nb_channel_items)

    def test_parent_items_not_listed_if_token_on_subchannel(self):
        header = {'HTTP_CHANNELTOKEN': self.subchanneltoken.token}
        response = self.anonymous_client.get(reverse('public_api_item_list'), {}, **header)

        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), self.nb_subchannel_items)

    def test_channel_hierarchy_is_given_as_attribute(self):
        header = {'HTTP_CHANNELTOKEN': self.subchanneltoken.token}
        response = self.anonymous_client.get(reverse('public_api_item_list'), {}, **header)
        data = response.data
        item = data[0]
        self.assertEqual(item['channel'], str(self.subchannel))
