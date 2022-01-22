import os

from django.conf import settings
from django.test import TestCase

from pilot.assets.tests import factories as assets_factories
from pilot.utils.test import MediaMixin


class FactoriesTests(MediaMixin, TestCase):
    """Test Asset Factories."""

    def test_asset_factory(self):
        """Test AssetFactory."""
        asset = assets_factories.AssetFactory.create()

        self.assertIsNotNone(asset.desk)
        self.assertIsNotNone(asset.title)
        self.assertEqual(asset.description, None)
        self.assertTrue(asset.file)
        # TODO : Test transloadit API which is responsible to generate metadata (thumbnail, width, ..)
        # self.assertTrue(asset.thumbnail)
        # self.assertEqual(asset.size, 125)
        # self.assertEqual(asset.height, 500)
        # self.assertEqual(asset.width, 500)
        # self.assertEqual(asset.orientation, 'portrait')
        self.assertIsNone(asset.license)
        self.assertIsNone(asset.copyright_duration)
        self.assertIsNone(asset.allowed_supports)

    def test_jpeg_asset_factory(self):
        """Test AssetFactory."""
        asset = assets_factories.JpegAssetFactory.create()

        self.assertTrue(asset.file)
        # TODO : Test transloadit API which is responsible to generate metadata (thumbnail, width, ..)
        # self.assertTrue(asset.thumbnail)
        # self.assertEqual(asset.size, 546)
        # self.assertEqual(asset.height, 10)
        # self.assertEqual(asset.width, 20)
        # self.assertEqual(asset.orientation, 'paysage')

    def test_txt_asset_factory(self):
        """Test AssetFactory."""
        asset = assets_factories.TxtAssetFactory.create()

        self.assertTrue(asset.file)
        # self.assertFalse(asset.thumbnail)
        # self.assertEqual(asset.size, len(TXT_FILE))
        self.assertIsNone(asset.height)
        self.assertIsNone(asset.width)

    def test_asset_file_path(self):
        """Test if file path and thumbnail path are correctly generated."""
        asset = assets_factories.AssetFactory.create()
        desk_id = str(asset.desk.id)
        id = str( asset.id)

        file_path = os.path.join(
            settings.MEDIA_ROOT,
            'assets',
            desk_id,
            id,
            '{}_{}_original'.format(desk_id, id)
        )
        self.assertEqual(asset.file.name, file_path)

        # This is currently provided by transloadit, cannot test it right
        # thumbnail_path = os.path.join(
        #     settings.MEDIA_ROOT,
        #     'assets',
        #     desk_id,
        #     id,
        #     '{}_{}_cover'.format(desk_id, id)
        # )
        # self.assertEqual(asset.thumbnail.name, thumbnail_path)
