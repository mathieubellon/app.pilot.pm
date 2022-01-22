import json
from unittest import skip

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from pilot.activity_stream.models import Activity
from pilot.assets.tests import factories as assets_factories
from pilot.items.models import Item
from pilot.projects.tests import factories as projects_factories
from pilot.channels.tests import factories as channels_factories
from pilot.items.tests import factories as items_factories
from pilot.item_types import initial_item_types
from pilot.item_types.tests.testing_item_type_definition import ADVANCED_TEST_SCHEMA
from pilot.integrations.tests import factories as api_factories
from pilot.targets.tests import factories as targets_factories
from pilot.workflow.initial_states import InitialStateNames
from pilot.utils.prosemirror.prosemirror import markdown
from pilot.utils.test import PilotAdminUserMixin, prosemirror_body
from pilot.item_types.tests import factories as item_types_factories


@skip('Public API is disabled for now')
class PublicApiTestMixin(object):
    ITEM_API_READ_ONLY_FIELDS = (
        'id',
        'url',
        'updated_at',
        'type',
        'publication_dt',
        'state_dates',
        'tags',
        'files',
        'project',
        'channel',
        'targets',
        'cfields'
    )
    ITEM_API_UPDATABLE_FIELDS = (
        'state',
    )
    ITEM_API_FIELDS = ITEM_API_READ_ONLY_FIELDS + ITEM_API_UPDATABLE_FIELDS

    def setUp(self):
        super(PublicApiTestMixin, self).setUp()

        self.anonymous_client = APIClient()
        self.auth_client = APIClient()

    def set_auth(self, token):
        self.auth_client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.token))

    def assert_common_api_item_fields(self, item):
        for field_name in self.ITEM_API_FIELDS:
            self.assertIn(field_name, item)


class PublicApiAuthTest(PublicApiTestMixin,
                        APITestCase):
    views_without_pk = (
        'public_api_channel_list_v2',
        'public_api_item_list_v2'
    )
    views_with_pk = (
        'public_api_item_detail_v2',
    )

    def test_auth(self):
        def test_url(url):
            # No token
            response = self.anonymous_client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            # Invalid token
            self.auth_client.credentials(HTTP_AUTHORIZATION='Token {}'.format("invalid"))
            response = self.auth_client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        for view_name in self.views_without_pk:
            test_url(reverse(view_name))

        for view_name in self.views_with_pk:
            test_url(reverse(view_name, kwargs={'pk': 1}))


class PublicApiItemTest(PublicApiTestMixin,
                        PilotAdminUserMixin,
                        APITestCase):
    """Test the public API for items"""
    longMessage = True

    def setUp(self):
        super(PublicApiItemTest, self).setUp()

        self.channel1 = channels_factories.ChannelFactory.create(desk=self.desk)
        self.channel2 = channels_factories.ChannelFactory.create(desk=self.desk)

        self.channel1token = api_factories.ApiTokenFactory.create(desk=self.desk,
                                                                  channels=[self.channel1])
        self.allchanneltoken = api_factories.ApiTokenFactory.create(desk=self.desk,
                                                                    channels=[self.channel1, self.channel2])

        # Create published and publication ready items for the two channel.
        self.number_of_published_items = 6
        self.number_of_publication_ready_items = 7

        self.published_items_channel1 = items_factories.ItemFactory.create_batch(
            size=self.number_of_published_items,
            desk=self.desk,
            channel=self.channel1,
            state=InitialStateNames.PUBLISHED
        )
        self.publication_ready_items_channel1 = items_factories.ItemFactory.create_batch(
            size=self.number_of_publication_ready_items,
            desk=self.desk,
            channel=self.channel1,
            state=InitialStateNames.PUBLICATION_READY
        )
        self.published_items_channel2 = items_factories.ItemFactory.create_batch(
            size=self.number_of_published_items,
            desk=self.desk,
            channel=self.channel2,
            state=InitialStateNames.PUBLISHED
        )
        self.publication_ready_items_channel2 = items_factories.ItemFactory.create_batch(
            size=self.number_of_publication_ready_items,
            desk=self.desk,
            channel=self.channel2,
            state=InitialStateNames.PUBLICATION_READY
        )

    def test_public_api_items_list(self):
        """Test the 'public_api_item_list'."""
        self.set_auth(self.allchanneltoken)
        url = reverse('public_api_item_list_v2')
        items_per_channel = self.number_of_publication_ready_items + self.number_of_published_items
        page_size = 10

        def assert_list_result(response, nb_item_expected):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            data = response.data
            self.assertEqual(data['count'], nb_item_expected)
            self.assertEqual(len(data['results']), min(page_size, nb_item_expected))
            self.assert_common_api_item_fields(data['results'][0])

        # Item list with all channels
        response = self.auth_client.get(url)
        assert_list_result(response, items_per_channel * 2)

        # Item list with one channel (filtered by query_param)
        response = self.auth_client.get(url, {'channel': self.channel1.id})
        assert_list_result(response, items_per_channel)

        # Item list with one state (filtered by query_param)
        response = self.auth_client.get(url, {'state': InitialStateNames.PUBLISHED})
        assert_list_result(response, self.number_of_published_items * 2)

        # Item list with one channel and one state (filtered by query_param)
        response = self.auth_client.get(url, {
            'channel': self.channel1.id,
            'state': InitialStateNames.PUBLISHED
        })
        assert_list_result(response, self.number_of_published_items)

        # Item list with one channel (filtered by token)
        self.set_auth(self.channel1token)
        response = self.auth_client.get(url)
        assert_list_result(response, items_per_channel)

    def test_public_api_item_retrieve(self):
        """Test the 'public_api_item_detail' with GET method"""
        project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            name="Awesome project"
        )

        target = targets_factories.TargetFactory.create(
            desk=self.desk,
            name="Awesome target"
        )

        asset = assets_factories.JpegAssetFactory.create(
            desk=self.desk,
            title="Awesome Asset",
            filetype="Image"
        )

        body = "Awesome content"
        item = items_factories.ItemFactory.create(
            desk=self.desk,
            project=project,
            channel=self.channel1,
            state=InitialStateNames.PUBLISHED,
            targets=[target],
            assets=[asset],
            json_content={
                'title': "Awesome title",
                'body': json.dumps(prosemirror_body(body))},
        )
        tags = ['Awesome tag', 'Mighty tag']
        item.tags.set(tags)

        self.set_auth(self.allchanneltoken)
        url = reverse('public_api_item_detail_v2', kwargs={'pk': item.pk})

        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item_json = response.data

        self.assert_common_api_item_fields(item_json)

        self.assertEqual(item_json['id'], item.id)
        self.assertIn(reverse('public_api_item_detail_v2', kwargs={'pk': item.pk}), item_json['url'])
        self.assertEqual(item_json['type'], {
            "is_custom": False,
            "technical_name": initial_item_types.ArticleItemType.technical_name,
            "name": initial_item_types.ArticleItemType.name
        })
        self.assertEqual(item_json['state'], InitialStateNames.PUBLISHED)
        self.assertSetEqual(set(item_json['tags']), set(tags))
        self.assertEqual(len(item_json['files']), 1)
        self.assertDictEqual(item_json['files'][0], {
            "url": asset.file_url,
            "title": asset.title,
            "filetype": "Image",
            "size": asset.size,
            "extension": "jpeg"
        })
        self.assertDictEqual(item_json['project'], {'id': project.id, 'name': project.name})
        self.assertDictEqual(item_json['channel'], {'id': self.channel1.id, 'name': self.channel1.name, 'parent': None})
        self.assertEqual(len(item_json['targets']), 1)
        self.assertDictEqual(item_json['targets'][0], {'id': target.id, 'name': target.name})

        # Check that ItemContent.title and .body are passed in the cfields dict
        cfields_dict = {cfield['field_name']: cfield for cfield in item_json['cfields']}

        self.assertEqual(cfields_dict['title']['field_content'], item.title)
        # self.assertEqual(cfields_dict['body']['field_content_json'], item.content['body'])
        self.assertEqual(cfields_dict['body']['field_content'], markdown(body))

        # Now test a custom type item
        item_type = item_types_factories.ItemTypeFactory.create(
            desk=self.desk,
            content_schema=ADVANCED_TEST_SCHEMA
        )
        item.item_type = item_type
        item.save()
        custom_data = {
            'title': 'Mighty Title',
            'body': json.dumps(prosemirror_body(u'Mighty content', is_strong=True)),
            'integer': 42,
            'float': 42.42,
            'char': 'char',
        }
        item.content = custom_data
        item.save()

        response = self.auth_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item_json = response.data

        self.assert_common_api_item_fields(item_json)

        cfields_dict = {cfield['field_name']: cfield for cfield in item_json['cfields']}

        self.assertEqual(cfields_dict['title']['field_content'], custom_data['title'])
        self.assertEqual(cfields_dict['body']['field_content'], '<p><strong>Mighty content</strong></p>\n')
        self.assertEqual(cfields_dict['integer']['field_content'], custom_data['integer'])
        self.assertEqual(cfields_dict['float']['field_content'], custom_data['float'])
        self.assertEqual(cfields_dict['char']['field_content'], custom_data['char'])

    def test_public_api_item_update(self):
        """Test the 'public_api_item_detail' with PATCH method"""
        old_state = InitialStateNames.PUBLICATION_READY
        new_state = InitialStateNames.PUBLISHED
        item = items_factories.ItemFactory.create(
            desk=self.desk,
            channel=self.channel1,
            state=old_state
        )
        item_pk = item.pk

        self.set_auth(self.allchanneltoken)
        url = reverse('public_api_item_detail_v2', kwargs={'pk': item_pk})

        response = self.auth_client.put(url, data={'state': new_state})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # The response contains the json for the updated item
        item_json = response.data
        self.assert_common_api_item_fields(item_json)
        self.assertEqual(item_json['state'], new_state)

        # The db instance is updated
        item = Item.objects.get(pk=item_pk)
        self.assertEqual(item.workflow_state.name, new_state)

        # An activity_stream has been created
        activity_stream = Activity.activities_for(item)
        self.assertEqual(1, len(activity_stream))

        # These attributes are read-only, and cannot be updated
        for field_name in self.ITEM_API_READ_ONLY_FIELDS:
            old_value = item_json[field_name]
            response = self.client.put(reverse('public_api_item_detail_v2', kwargs={'pk': item_pk}),
                                       data={field_name: 'meh'},
                                       format='json')
            new_value = item_json[field_name]
            self.assertEqual(old_value, new_value, msg="field '{}'".format(field_name))


class PublicApiChannelsHierarchyTest(PublicApiTestMixin,
                                     PilotAdminUserMixin,
                                     APITestCase):
    """Test the public API with hierarchies of channels"""

    def setUp(self):
        super(PublicApiChannelsHierarchyTest, self).setUp()

        self.channel = channels_factories.ChannelFactory.create(desk=self.desk)
        self.subchannel = channels_factories.ChannelFactory.create(desk=self.desk,
                                                                   parent=self.channel)
        self.channel2 = channels_factories.ChannelFactory.create(desk=self.desk)

        self.channeltoken = api_factories.ApiTokenFactory.create(desk=self.desk,
                                                                 channels=[self.channel])
        self.subchanneltoken = api_factories.ApiTokenFactory.create(desk=self.desk,
                                                                    channels=[self.subchannel])
        self.allchanneltoken = api_factories.ApiTokenFactory.create(desk=self.desk,
                                                                    channels=[self.channel, self.channel2])

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
        self.nb_channel2_items = 3
        self.channel_items = items_factories.ItemFactory.create_batch(
            size=self.nb_channel2_items,
            desk=self.desk,
            channel=self.channel2,
            state=InitialStateNames.PUBLICATION_READY
        )

    # =============================================================
    # Tests on /publicapi/channels/
    # =============================================================
    def test_subchannel_are_listed_if_token_on_parent(self):
        self.set_auth(self.channeltoken)
        response = self.auth_client.get(reverse('public_api_channel_list_v2'))
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], self.channel.name)
        self.assertEqual(data[1]['name'], self.subchannel.name)

    def test_parent_not_listed_if_token_on_subchannel(self):
        self.set_auth(self.subchanneltoken)
        response = self.auth_client.get(reverse('public_api_channel_list_v2'))
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], self.subchannel.name)

    def test_all_channel_are_listed(self):
        self.set_auth(self.allchanneltoken)
        response = self.auth_client.get(reverse('public_api_channel_list_v2'))
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 3)

    # =============================================================
    # Tests on /publicapi/items/
    # =============================================================
    def test_subchannel_items_are_listed_if_token_on_parent(self):
        self.set_auth(self.channeltoken)
        response = self.auth_client.get(reverse('public_api_item_list_v2'))

        items = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(items), self.nb_subchannel_items + self.nb_channel_items)

    def test_parent_items_not_listed_if_token_on_subchannel(self):
        self.set_auth(self.subchanneltoken)
        response = self.auth_client.get(reverse('public_api_item_list_v2'))

        items = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(items), self.nb_subchannel_items)
