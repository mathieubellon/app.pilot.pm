import json

from django.urls import reverse

from rest_framework.test import APITestCase

from pilot.items.tests import factories as items_factories
from pilot.utils.test import PilotAdminUserMixin, prosemirror_body
from pilot.items.tests.test_api import ItemAPIMixin, API_ITEMS_DETAIL_URL


class ItemContentApiTest(ItemAPIMixin, PilotAdminUserMixin, APITestCase):
    """ Test the content API on a single Item """

    def test_item_edit_content(self):
        """Test edit item content with general type"""

        item = items_factories.ConfirmedItemFactory.create(desk=self.desk)

        # Refresh the cached item instance to ensure to fetch the RelatedFactory results
        # (i.e. the EditSession obj).
        item = Item.objects.get(pk=item.pk)
        session = EditSession.objects.get(item=item)
        self.assertEqual(item.title, session.title)
        self.assertEqual(item.content['body'], session.content['body'])

        api_item_url = reverse(API_ITEMS_DETAIL_URL, kwargs={'pk': item.pk})

        # Test PUT
        content = {
            'title': 'New title',
            'body': prosemirror_body(u'New content'),
        }
        update_data = {
            'content': content
        }
        response = self.client.put(api_item_url, data=update_data, format='json')
        self.assertEqual(response.status_code, 200)

        # Check edited Item.
        item = Item.objects.get(pk=item.pk)
        self.assertEqual(item.content['body'], content['body'])
        self.assertEqual(item.title, content['title'])

        # Check the created EditSession.
        session = item.last_session
        self.assertEqual(session.content['body'], item.content['body'])
        self.assertEqual(session.title, item.title)
        self.assertEqual(session.title, content['title'])
        self.assertEqual(session.content['body'], content['body'])
        self.assertEqual(session.version, '1.1')

    def test_tweet_item_edit_content(self):
        """Test edit tweet item content."""

        item = items_factories.ConfirmedItemTweetFactory.create(desk=self.desk)

        # Refresh the cached item instance to ensure to fetch the RelatedFactory results
        # (i.e. the EditSession obj).
        item = Item.objects.get(pk=item.pk)
        session = EditSession.objects.get(item=item)
        self.assertEqual(item.title, session.title)
        self.assertEqual(item.content['body'], session.content['body'])

        api_item_url = reverse(API_ITEMS_DETAIL_URL, kwargs={'pk': item.pk})

        # Test PUT too long content.
        content = {
            'title': u'New title ünicôdé',
            'body': prosemirror_body(u'x' * 281),  # Tweet max length == 280
        }
        update_data = {
            'content': content
        }

        response = self.client.put(api_item_url, data=update_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {u'content': {u'body': [
            u'Contenu trop long. Twitter autorise seulement 280 signes ( 281 signes saisis)'
        ]}})
        # Check the ite has not been edited
        item = Item.objects.get(pk=item.pk)
        self.assertNotEqual(item.content['body'], content['body'])

        # Test PUT with correct length.
        content['body'] = prosemirror_body(u'î' * 280)
        response = self.client.put(api_item_url, data=update_data, format='json')
        self.assertEqual(response.status_code, 200)

        # Check edited Item.
        item = Item.objects.get(pk=item.pk)
        self.assertEqual(item.content['body'], content['body'])
        self.assertTrue(isinstance(item.content['body'],dict))
        self.assertEqual(item.title, content['title'])

        # Check the created EditSession.
        session = item.last_session
        self.assertEqual(session.content['body'], item.content['body'])
        self.assertEqual(session.title, item.title)
        self.assertEqual(session.title, content['title'])
        self.assertEqual(session.content['body'], content['body'])
        self.assertEqual(session.version, '1.1')

    def test_facebook_item_edit_content(self):
        """Test edit facebook item content."""

        item = items_factories.ConfirmedItemFacebookFactory.create(desk=self.desk)

        # Refresh the cached item instance to ensure to fetch the RelatedFactory results
        # (i.e. the EditSession obj).
        item = Item.objects.get(pk=item.pk)
        session = EditSession.objects.get(item=item)
        self.assertEqual(item.title, session.title)

        api_item_url = reverse(API_ITEMS_DETAIL_URL, kwargs={'pk': item.pk})

        # Test PUT too long content.
        content = {
            'title': u'New title ünicôdé',
            'body': prosemirror_body(u'x' * 10001)
        }
        update_data = {
            'content': content
        }

        response = self.client.put(api_item_url, data=update_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {u'content': {u'body': [
            u'Contenu trop long. Facebook autorise seulement 10000 signes ( 10001 signes saisis)'
        ]}})
        # Check the ite has not been edited
        item = Item.objects.get(pk=item.pk)
        self.assertNotEqual(json.dumps(item.content['body']), content['body'])

        # Test PUT with correct length.
        content['body'] = {"type":"doc","content":[{"type":"paragraph","content":[{"type":"text","text": u'î' * 9850}]}]}
        response = self.client.put(api_item_url, data=update_data, format='json')
        self.assertEqual(response.status_code, 200, response.data)

        # Check edited Item.
        item = Item.objects.get(pk=item.pk)
        self.assertEqual(item.content['body'], content['body'])
        self.assertEqual(item.title, content['title'])

        # Check the created EditSession.
        session = item.last_session
        self.assertEqual(session.content['body'], item.content['body'])
        self.assertEqual(session.title, item.title)
        self.assertEqual(session.title, content['title'])
        self.assertEqual(session.content['body'], content['body'])
        self.assertEqual(session.version, '1.1')
