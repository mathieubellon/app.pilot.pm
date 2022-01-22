import base64
import json
import re
import logging
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone

from pilot.assets.models import Asset
from pilot.assets.utils import get_uploaded_file_attributes, start_transloadit_conversion
from pilot.items.models import Item, ItemSnapshot
from pilot.utils.s3 import upload_s3_file

logger = logging.getLogger(__name__)

b64_regex = re.compile(r'"data:image/(.*?);base64,(.*?)"')


class Command(BaseCommand):

    query = """
    SELECT id, desk_id, json_content
    FROM items_item
    WHERE json_content::TEXT LIKE '%%base64,%%'
    """

    def handle(self, verbosity=0, **kwargs):
        logger.info(f"[Command Start] {' '.join(sys.argv[1:])}")

        counter = 0
        for item in Item.objects.raw(self.query):
            Migrator(item).migrate_base64_encoded_images()
            counter +=1
            if counter%10==0:
                print(f'{counter} done...')

        logger.info(f"[Command End] {' '.join(sys.argv[1:])}")

class Migrator(object):
    def __init__(self, item):
        self.item = item
        # b64_string => s3 url
        self.b64_strings = {}

    def upload_b64_image(self, b64_string, extension):
        index = len(self.b64_strings) + 1
        file_name = f'item{self.item.id}-image{index}.{extension}'

        asset = Asset(
            desk_id=self.item.desk_id,
            in_media_library=False,
            updated_at=timezone.now(),
            **get_uploaded_file_attributes(file_name)
        )
        models.Model.save(asset)
        self.item.assets.add(asset)

        file = base64.b64decode(b64_string)
        upload_s3_file(asset.originalpath, file, file_name)

        asset.file = asset.originalpath
        conversion_data = start_transloadit_conversion(asset)
        asset.update_conversion_data(conversion_data)
        models.Model.save(asset)

        return settings.AWS_S3_BASE_URL + asset.image_working_path

    def migrate_one_item_content(self, item_content):
        new_content = {}
        for field_name, value in item_content.json_content.items():
            string_value = json.dumps(value)
            matches = b64_regex.findall(string_value)
            for extension, match in matches:
                if match not in self.b64_strings:
                    self.b64_strings[match] = self.upload_b64_image(match, extension)
                string_value = b64_regex.sub(f'"{self.b64_strings[match]}"', string_value, count=1)

            new_content[field_name] = json.loads(string_value)

        item_content.json_content = new_content

        # Don't use directly item_content.save, this would create snapshots and launch jobs on Item
        # and trigger warnings on item_snapshots
        models.Model.save(item_content)

    def migrate_base64_encoded_images(self):
        self.migrate_one_item_content(self.item)
        for snapshot in ItemSnapshot.objects.filter(item=self.item):
            self.migrate_one_item_content(snapshot)
