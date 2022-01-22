import factory

from pilot.assets.models import Asset
from pilot.desks.tests import factories as desks_factories
from pilot.utils.test import PNG_IMG_FILE, JPEG_IMG_FILE, TXT_FILE


class AssetFactory(factory.DjangoModelFactory):
    """Base Asset factory."""
    FACTORY_FOR = Asset

    desk = factory.SubFactory(desks_factories.DeskFactory)
    title = factory.Sequence("Asset {0}".format)
    file = factory.django.FileField(data=PNG_IMG_FILE.decode('base64'), filename='test.png')
    in_media_library = True


class JpegAssetFactory(AssetFactory):
    file = factory.django.FileField(data=JPEG_IMG_FILE.decode('base64'), filename='test.jpeg')


class TxtAssetFactory(AssetFactory):
    file = factory.django.FileField(data=TXT_FILE.encode('utf8'), filename='test.txt')
