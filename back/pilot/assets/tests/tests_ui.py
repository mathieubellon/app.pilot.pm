import json
from unittest import skip

import boto

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import TestCase

from pilot.assets.tests import factories as assets_factories
from pilot.items.tests import factories as item_factories
from pilot.utils.test import (PilotAdminUserMixin,
                              PilotRestrictedEditorUserMixin,
                              MediaMixin, PNG_IMG_FILE, JPEG_IMG_FILE,
                              TXT_FILE)


def get_file_from_base64(filename, data):
    if (settings.DEFAULT_FILE_STORAGE ==
            'storages.backends.s3boto.S3BotoStorage'):
        s3 = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                             settings.AWS_SECRET_ACCESS_KEY)
        bucket = s3.lookup(settings.AWS_STORAGE_BUCKET_NAME)
        k = boto.s3.key.Key(bucket)
        k.key = 'assets/tmp/{filename}'.format(filename=filename)
        k.set_contents_from_string(data)
        return k.key
    else:
        return SimpleUploadedFile(filename, data)


class AssetsUiTest(MediaMixin, PilotAdminUserMixin, TestCase):
    """Test CRUD on Asset objects."""

    def test_asset_details(self):
        """Test the details view of an asset."""

        asset = assets_factories.AssetFactory.create(desk=self.desk)

        # Test GET.
        response = self.client.get('/assets/{pk}/'.format(pk=asset.pk))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(asset, response.context['asset'])

    def test_asset_details_with_hidden_or_trashed_items(self):
        """Test the details view of an asset."""

        asset = assets_factories.AssetFactory.create(desk=self.desk)

        item_1 = item_factories.ItemFactory.create(desk=self.desk)
        item_2 = item_factories.ItemFactory.create(desk=self.desk)
        item_1.assets.add(asset)
        item_2.assets.add(asset)

        url = reverse('api-assets-detail', kwargs={'pk': asset.id})

        # Test GET.
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        item_ids = [item['id'] for item in json.loads(response.content)['items']]
        self.assertIn(item_1.id, item_ids)
        self.assertIn(item_2.id, item_ids)

        # One item in trash. Test GET.
        item_1.put_in_trash()
        response = self.client.get(url, format='json')
        item_ids = [item['id'] for item in json.loads(response.content)['items']]
        # Item1 not visible
        self.assertNotIn(item_1.id, item_ids)
        # Item2 visible
        self.assertIn(item_2.id, item_ids)

        # Both items in trash. Test GET.
        item_2.put_in_trash()
        response = self.client.get(url, format='json')
        item_ids = [item['id'] for item in json.loads(response.content)['items']]
        # Item1 not visible
        self.assertNotIn(item_1.id, item_ids)
        # Item2 not visible
        self.assertNotIn(item_2.id, item_ids)

        # Item2 hidden. Test GET.
        item_2.hide()
        response = self.client.get(url, format='json')
        item_ids = [item['id'] for item in json.loads(response.content)['items']]
        # Item1 not visible
        self.assertNotIn(item_1.id, item_ids)
        # Item2 not visible
        self.assertNotIn(item_2.id, item_ids)

        # Item1 restored. Test GET.
        item_1.restore_from_trash()
        response = self.client.get(url, format='json')
        item_ids = [item['id'] for item in json.loads(response.content)['items']]
        # Item1 visible
        self.assertIn(item_1.id, item_ids)
        # Item2  not visible
        self.assertNotIn(item_2.id, item_ids)

    @skip("View obsoleted by the new Vue.js UI")
    def test_asset_add(self):
        """Test asset add."""

        # Test GET.
        response = self.client.get('/assets/add/')
        self.assertEqual(response.status_code, 200)

        # Check that in_media_library input is not present
        self.assertNotContains(response, 'name="in_media_library"')

        # Test POST.
        post_data = {
            'file': get_file_from_base64('test.png', PNG_IMG_FILE.decode('base64')),
            'title': u'Asset title ünicôdé',
            'description': u'Asset description ünicôdé',
            'license': 1,
            'copyright_duration': 5,
            'allowed_supports': 1,
        }
        response = self.client.post('/assets/add/', data=post_data)
        self.assertEqual(response.status_code, 302)

        # Check added Asset.
        asset = Asset.objects.get(title=post_data['title'])
        self.assertRedirects(response, '/assets/{0}/'.format(asset.id))

        self.assertEqual(asset.desk, self.desk)
        fmt = ('assets/{desk_id}/{id}/'
               '{desk_id}_{id}_original.png')
        path = fmt.format(desk_id=asset.desk.id, id=asset.id)
        self.assertEqual(asset.file.name, path)
        fmt = ('assets/{desk_id}/{id}/'
               '{desk_id}_{id}_cover.png')
        path = fmt.format(desk_id=asset.desk.id, id=asset.id)
        # self.assertEqual(asset.thumbnail.name, path)
        self.assertEqual(asset.title, post_data['title'])
        # TODO : Test transloadit API which is responsible to generate metadata (thumbnail, width, ..)
        # self.assertEqual(asset.size, len(PNG_IMG_FILE.decode('base64')))
        # self.assertEqual(asset.width, 500)
        # self.assertEqual(asset.height, 500)
        # self.assertEqual(asset.orientation, 'portrait')
        # TODO for the time being those fields have been removed
        # self.assertEqual(asset.description, post_data['description'])
        # self.assertEqual(asset.license, post_data['license'])
        # self.assertEqual(asset.copyright_duration,
        # post_data['copyright_duration'])
        # self.assertEqual(asset.allowed_supports, post_data['allowed_supports'])

    @skip("View obsoleted by the new Vue.js UI")
    def test_asset_add_jpeg(self):
        """Test asset add with a jpeg image."""

        # Test POST.
        post_data = {
            'title': u'JPEG image',
            'file': get_file_from_base64('test.jpeg',
                                         JPEG_IMG_FILE.decode('base64')),
        }
        response = self.client.post('/assets/add/', data=post_data)
        self.assertEqual(response.status_code, 302)

        # Check added Asset.
        asset = Asset.objects.get(title=post_data['title'])
        self.assertRedirects(response, '/assets/{0}/'.format(asset.id))
        self.assertEqual(asset.desk, self.desk)
        fmt = ('assets/{desk_id}/{id}/'
               '{desk_id}_{id}_original.jpeg')
        path = fmt.format(desk_id=asset.desk.id, id=asset.id)
        self.assertEqual(asset.file.name, path)
        fmt = ('assets/{desk_id}/{id}/'
               '{desk_id}_{id}_cover.png')
        path = fmt.format(desk_id=asset.desk.id, id=asset.id)
        # self.assertEqual(asset.thumbnail.name, path)
        self.assertEqual(asset.title, post_data['title'])
        # self.assertEqual(asset.size, len(JPEG_IMG_FILE.decode('base64')))
        # self.assertEqual(asset.width, 20)
        # self.assertEqual(asset.height, 10)
        # self.assertEqual(asset.orientation, 'paysage')

    @skip("View obsoleted by the new Vue.js UI")
    def test_asset_add_txt(self):
        """Test asset add with a text file."""

        # Test POST.
        post_data = {
            'title': u'Text',
            'file': get_file_from_base64('test.txt',
                                         TXT_FILE.encode('utf8')),
        }
        response = self.client.post('/assets/add/', data=post_data)
        self.assertEqual(response.status_code, 302)

        # Check added Asset.
        asset = Asset.objects.get(title=post_data['title'])
        self.assertRedirects(response, '/assets/{0}/'.format(asset.id))
        self.assertEqual(asset.desk, self.desk)
        fmt = ('assets/{desk_id}/{id}/'
               '{desk_id}_{id}_original.txt')
        path = fmt.format(desk_id=asset.desk.id, id=asset.id)
        self.assertEqual(asset.file.name, path)
        self.assertEqual(asset.title, post_data['title'])
        # self.assertEqual(asset.size, len(TXT_FILE.encode('utf8')))
        self.assertIsNone(asset.width)
        self.assertIsNone(asset.height)

    @skip("View obsoleted by the new Vue.js UI")
    def test_asset_edit(self):
        """Test edit asset."""

        asset = assets_factories.AssetFactory.create(desk=self.desk)

        url = '/assets/{pk}/edit/'.format(pk=asset.pk)

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        post_data = {
            'file': get_file_from_base64('test.jpeg',
                                         JPEG_IMG_FILE.decode('base64')),
            'title': u'New title',
            'description': u'New description',
            'license': 1,
            'copyright_duration': 5,
            'allowed_supports': 1,
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, asset.get_absolute_url())

        # Check edited Asset.
        asset = Asset.objects.get(pk=asset.pk)
        fmt = 'assets/{desk_id}/{id}/{desk_id}_{id}_original.jpeg'
        path = fmt.format(desk_id=asset.desk.id, id=asset.id)
        self.assertEqual(asset.file.name, path)
        fmt = ('assets/{desk_id}/{id}/'
               '{desk_id}_{id}_cover.png')
        path = fmt.format(desk_id=asset.desk.id, id=asset.id)
        # self.assertEqual(asset.thumbnail.name, path)
        self.assertEqual(asset.title, post_data['title'])
        self.assertEqual(asset.description, post_data['description'])
        # self.assertEqual(asset.size, len(JPEG_IMG_FILE.decode('base64')))
        # self.assertEqual(asset.width, 20)
        # self.assertEqual(asset.height, 10)
        # self.assertEqual(asset.orientation, 'paysage')
        # TODO for the time being those fields have been removed
        # self.assertEqual(asset.license, post_data['license'])
        # self.assertEqual(asset.copyright_duration,
        # post_data['copyright_duration'])
        # self.assertEqual(asset.allowed_supports, post_data['allowed_supports'])

    @skip("View obsoleted by the new Vue.js UI")
    def test_asset_remove_thumbnail(self):
        """Test fi thumbnail is removed if need be."""

        asset = assets_factories.AssetFactory.create(desk=self.desk)

        url = '/assets/{pk}/edit/'.format(pk=asset.pk)

        # Test POST.
        post_data = {
            'file': get_file_from_base64('test.txt',
                                         TXT_FILE.encode('utf8')),
            'title': u'Text',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, asset.get_absolute_url())

        # Check edited Asset.
        asset = Asset.objects.get(pk=asset.pk)
        fmt = 'assets/{desk_id}/{id}/{desk_id}_{id}_original.txt'
        path = fmt.format(desk_id=asset.desk.id, id=asset.id)
        self.assertEqual(asset.file.name, path)
        # self.assertEqual(asset.size, len(TXT_FILE))
        self.assertIsNone(asset.width)
        self.assertIsNone(asset.height)


class ItemsUiTestRestrictedEditorPermsTest(MediaMixin, PilotRestrictedEditorUserMixin, TestCase):
    """Test access perms for a `restricted editor` user."""

    @skip("View obsoleted by the new Vue.js UI")
    def test_access_perms(self):
        assets_factories.AssetFactory.create(desk=self.desk)

        # Should be able to view the assets list.
        response = self.client.get('/assets/')
        self.assertEqual(response.status_code, 200)

        # Should be able to add an asset.
        response = self.client.get('/assets/add/')
        self.assertEqual(response.status_code, 200)
