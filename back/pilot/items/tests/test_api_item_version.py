import json
from django.urls import reverse
from rest_framework.test import APITestCase
from pilot.items.tests import factories as items_factories

from pilot.utils.test import PilotAdminUserMixin


class ItemApiItemAddTest(PilotAdminUserMixin, APITestCase):
    def test_item_versions_list(self):
        """Test the list of versions of an item content."""

        item = items_factories.ConfirmedItemFactory.create(desk=self.desk)

        items_factories.EditSessionFactory.create_batch(size=3, item=item)

        # 3 EditSession via EditSessionFactory + 1 EditSession via ConfirmedItemFactory.
        self.assertEqual(4, item.sessions.all().count())

        url = reverse('api_item_versions_list', kwargs={'item_pk': item.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        versions = json.loads(response.content)
        self.assertEqual(4, len(versions))
        [self.assertTrue(key in versions[0].keys(), (key, versions[0])) for key in ['id', 'created_by', 'version']]
        version_ids = map(lambda x: x['version'], versions)
        self.assertEqual([u'1.3', u'1.2', u'1.1', u'1.0'], version_ids)
