from django.urls import reverse
from django.test import TestCase

from pilot.items.tests import factories as items_factories
from pilot.utils.test import PilotAdminUserMixin


class ItemsExportTest(PilotAdminUserMixin, TestCase):
    """Test Item export formats."""

    def test_item_export_docx(self):
        item = items_factories.ItemFactory.create(desk=self.desk)
        response = self.client.get("%s?type=docx" % reverse('api-items-export', kwargs={'pk': item.pk}))
        #from pydocx import Docx2Html
        from io import StringIO
        buf = StringIO()
        buf.write(response.content)
        #html = Docx2Html(buf).parsed
        self.assertIn('<body><p>Item ID = %s' % item.pk, html)
