import json

from django.urls import reverse
from rest_framework.test import APITestCase

from pilot.targets.tests import factories as targets_factories
from pilot.utils.test import PilotAdminUserMixin


class TargetFilterApiTest(PilotAdminUserMixin, APITestCase):
    """Test the API for channels"""
    URL = 'targets-list'
    TARGET_API_FIELDS = ['id', 'name']

    def setUp(self):
        super(TargetFilterApiTest, self).setUp()
        self.url = reverse(self.URL)

    def test_list(self):
        targets_factories.TargetFactory.create_batch(size=3, desk=self.desk)
        content = self.content()
        self.assertEqual(3, len(content))
        self.assertEqual(self.TARGET_API_FIELDS, content[0].keys())

    def test_api_targets_list_filter_by_name(self):
        for name in ["Canal génial", "Canal génial", "Canal genial"]:
            targets_factories.TargetFactory.create(desk=self.desk, name=name)

        targets = self.content(filter = {'name': "genia"})
        self.assertEqual(1, len(targets))

        targets = self.content(filter = {'name': "génia"})
        self.assertEqual(2, len(targets))

    def content(self, filter=None):
        response = self.client.get(self.url, data=filter, format='json')
        return json.loads(response.content)
