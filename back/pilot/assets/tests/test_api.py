import json
from unittest import skip

from django.urls import reverse
from rest_framework.test import APITestCase

from pilot.pilot_users.tests import factories as pilot_users_factories
from pilot.assets.tests import factories as assets_factories
from pilot.items.tests import factories as items_factories
from pilot.utils.test import PilotAdminUserMixin
from django.contrib.contenttypes.models import ContentType
from pilot.activity_stream.models import Activity


class AssetsListApiTest(PilotAdminUserMixin, APITestCase):
    """Test the API for assets"""

    ASSET_API_READ_ONLY_FIELDS = ('id', 'url', 'file_url',
                                  'title', 'filetype', 'extension', 'created_at',
                                  'in_media_library', 'items', 'is_file_asset', 'is_image')
    ASSET_API_UPDATABLE_FIELDS = ()
    ASSET_API_FIELDS = ASSET_API_READ_ONLY_FIELDS + ASSET_API_UPDATABLE_FIELDS

    def setUp(self):
        super(AssetsListApiTest, self).setUp()

        self.list_url = reverse('api-assets-list')

        self.restricted_user = pilot_users_factories.RestrictedEditorFactory.create(password='password')
        self.organization.users.add(self.restricted_user)
        self.desk.users.add(self.restricted_user)

        self.assets1 = assets_factories.AssetFactory.create_batch(size=15,
                                                                  desk=self.desk,
                                                                  title="Test title",
                                                                  description="Test description",
                                                                  filetype='word')

        self.assets2 = assets_factories.AssetFactory.create_batch(size=15,
                                                                  desk=self.desk,
                                                                  title="Test titlé",
                                                                  description="Test descriptïon",
                                                                  filetype='pdf')

        self.assets3 = assets_factories.AssetFactory.create_batch(size=9,
                                                                  desk=self.desk,
                                                                  title="Test titlé",
                                                                  description="Test descriptïon",
                                                                  filetype='image')
        self.item = items_factories.ItemFactory.create(desk=self.desk)

        for a in self.assets3:
            self.item.assets.add(a)
        self.item.save()

        # Not in_media_library should not be sent by the library API
        self.not_library_assets = assets_factories.AssetFactory.create_batch(size=6,
                                                                             desk=self.desk,
                                                                             title="Test titlé",
                                                                             description="Test descriptïon",
                                                                             in_media_library=False)

        self.library_assets = (self.assets1 + self.assets2 + self.assets3)
        self.all_assets = (self.library_assets + self.not_library_assets)

        # Assets on another desk should not be sent by the asset API
        assets_factories.AssetFactory.create_batch(size=2,
                                                   title="Test titlé",
                                                   description="Test descriptïon")

        self.item_content_type = ContentType.objects.get_for_model(Item)

    def assert_common_api_item_fields(self, item):
        for field_name in self.ASSET_API_FIELDS:
            self.assertIn(field_name, item)

    def test_api_assets_list(self):
        # Standard list API
        response = self.client.get(self.list_url, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(self.all_assets), content['count'])
        self.assertEqual((len(self.all_assets) / ASSET_LIST_PAGE_SIZE) + 1, content['num_pages'])

        self.assert_common_api_item_fields(content['objects'][0])

        # Putting items in trash should not change visibility of assets
        self.item.put_in_trash()
        response = self.client.get(self.list_url, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(self.all_assets), content['count'])

        # Hiding items should not change visibility of assets
        self.item.hide()
        response = self.client.get(self.list_url, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(self.all_assets), content['count'])

    def test_api_assets_library(self):
        # Library API : list limited to in_media_library assets
        library_url = reverse('api-assets-library')
        response = self.client.get(library_url, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(self.library_assets), content['count'])
        self.assertEqual((len(self.library_assets) / ASSET_LIST_PAGE_SIZE) + 1, content['num_pages'])

        self.assert_common_api_item_fields(content['objects'][0])

    def test_api_assets_delete(self):
        asset = self.all_assets[0]
        delete_url = reverse('api-assets-detail', args=(asset.pk,))

        response = self.client.delete(delete_url, format='json')
        self.assertEqual(response.status_code, 204)

        # No more asset with this id in the db
        self.assertEqual(Asset.objects.filter(id=asset.pk).count(), 0)

    def test_api_assets_link(self):
        asset = self.all_assets[0]
        link_url = reverse('api-assets-link', args=(asset.pk,))

        # The asset is initially not linked to the item
        self.assertNotIn(asset, self.item.assets.all())

        post_data = {
            'content_type_id': self.item_content_type.id,
            'object_id': self.item.id
        }
        response = self.client.post(link_url, post_data, format='json')
        self.assertEqual(response.status_code, 200)

        # Refresh item data
        item = Item.objects.get(pk=self.item.pk)
        # The asset is now linked to the item
        self.assertIn(asset, item.assets.all())

        # An activity_stream has been created
        activity_stream = Activity.activities_for(item)
        self.assertEqual(1, len(activity_stream))

        # We can try to link it again, without errors
        response = self.client.post(link_url, post_data, format='json')
        self.assertEqual(response.status_code, 200)

        # Cannot link to an asset not in the media library
        not_library_asset = self.not_library_assets[0]
        link_url = reverse('api-assets-link', args=(not_library_asset.pk,))
        response = self.client.post(link_url, post_data, format='json')
        self.assertContains(response, "Cannot link", status_code=400)

    def test_api_assets_unlink(self):
        asset = self.item.assets.all()[0]
        unlink_url = reverse('api-assets-unlink', args=(asset.pk,))

        # The asset is initially linked to the item
        self.assertIn(asset, self.item.assets.all())

        post_data = {
            'content_type_id': self.item_content_type.id,
            'object_id': self.item.id
        }
        response = self.client.post(unlink_url, post_data, format='json')
        self.assertEqual(response.status_code, 200)

        # Refresh item data
        item = Item.objects.get(pk=self.item.pk)
        # The asset is now not linked to the item
        self.assertNotIn(asset, item.assets.all())

        # An activity_stream has been created
        activity_stream = Activity.activities_for(item)
        self.assertEqual(1, len(activity_stream))

        # We cannot try to link it again, that's an error
        response = self.client.post(unlink_url, post_data, format='json')
        self.assertContains(response, "Cannot unlink", status_code=400)

    @skip("Should be adapted to Asset creation by UUID")
    def test_api_create_asset(self):
        create_url = reverse('api-assets-list')
        post_data = {
            'content_type_id': self.item_content_type.id,
            'object_id': self.item.id,
            'title': 'a photo',
            'items': [],
            'file': '/tmp/test.png',
        }
        response = self.client.post(create_url, post_data, format='json')
        self.assertEqual(response.status_code, 201)
        asset = json.loads(response.content)
        self.assertEqual('a photo', asset['title'])
        self.assertEqual([self.item.id],  asset['items'])

    def test_api_assets_list_filter_by_title(self):
        # Test with special characters
        assets_factories.AssetFactory.create(desk=self.desk, title="Asset génial")
        assets_factories.AssetFactory.create(desk=self.desk, title="Asset genial")

        # Filter by name
        filter = {'q': "genia"}
        response = self.client.get(self.list_url, data=filter, format='json')
        content = json.loads(response.content)

        # Both accentuated and unaccentuated should come back
        self.assertEqual(2, content['count'])
        api_asset = content['objects'][0]
        self.assert_common_api_item_fields(api_asset)

        # Again, but with accentuated search
        filter = {'q': "génia"}
        response = self.client.get(self.list_url, data=filter, format='json')
        content = json.loads(response.content)
        # Both accentuated and unaccentuated should come back
        self.assertEqual(2, content['count'])
