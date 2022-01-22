import datetime
import copy
from unittest.case import skip

from django.urls import reverse
from django.test import TestCase
from django.utils.translation import activate

from rest_framework.test import APITestCase

from pilot.items.tests import factories as items_factories
from pilot.item_types import item_content_fields, initial_item_types
from pilot.items.tests.test_api import API_ITEMS_DETAIL_URL
from pilot.utils.test import PilotEditorUserMixin, PilotAdminUserMixin, prosemirror_body_string
from pilot.item_types.tests.testing_item_type_definition import SIMPLE_TEST_SCHEMA

from pilot.item_types.tests import factories


class ItemTypeEditUiTest(PilotEditorUserMixin, APITestCase):
    """Specific tests for custom type (json) edition."""

    def setUp(self):
        activate('fr')
        super(ItemTypeEditUiTest, self).setUp()

        self.content_schema = copy.deepcopy(SIMPLE_TEST_SCHEMA)

        self.item_type = factories.ItemTypeFactory.create(
            desk=self.desk,
            content_schema=self.content_schema,
        )
        self.item = items_factories.ItemFactory.create(
            desk=self.desk,
            channel=None,
            item_type=self.item_type,
            content={
                'integer': 42,
                'email': '42@42.com',
                'char': '42',
            },
        )
        self.api_edit_url = reverse(API_ITEMS_DETAIL_URL, kwargs={'pk': self.item.pk})

    def test_missing_custom_type_data(self):
        """Submit form without required custom type data."""

        update_data = {
            'content': {
                'title': 'Title',
                'body':  prosemirror_body_string(u'Content'),
            }
        }
        response = self.client.put(self.api_edit_url, data=update_data, format='json')
        self.assertEqual(response.status_code, 400)

        required_error = 'Ce champ est obligatoire.'
        self.assertEqual(response.data, {u'content': {
            'integer': [required_error],
            'email': [required_error],
            'char': [required_error]
        }})

    def test_custom_type_data_validation(self):
        """Submit form with incorrect custom type data."""

        update_data = {
            'content': {
                'title': 'Title',
                'body':  prosemirror_body_string(u'Content'),
                'integer': 'string',
                'email': 'string',
                'char': 'char',
            }
        }
        response = self.client.put(self.api_edit_url, data=update_data, format='json')
        self.assertEqual(response.status_code, 400)

        self.assertEqual(response.data, {u'content': {
            'integer': ['Un nombre entier valide est requis.'],
            'email': ['Saisissez une adresse email valable.']
        }})

    def test_item_edit_with_custom_type(self):
        """Submit form with correct custom type data."""

        update_data = {
            'content': {
                'title': 'Title',
                'body':  prosemirror_body_string(u'Content'),
                'integer': 42,
                'email': '42@42.com',
                'char': 'New 42',
            }
        }
        response = self.client.put(self.api_edit_url, data=update_data, format='json')
        self.assertEqual(response.status_code, 200)

        item = Item.objects.get(pk=self.item.pk)
        self.assertIsNotNone(item.content)
        self.assertEqual(item.content['integer'], 42)
        self.assertEqual(item.content['email'], '42@42.com')
        self.assertEqual(item.content['char'], 'New 42')

    def test_create_new_version(self):
        """Create new revision of an item with a custom type."""

        # One snapshot before the edition
        sessions = EditSession.objects.filter(item=self.item)
        self.assertEqual(1, sessions.count())

        update_data = {
            'content': {
                'title': 'Title',
                'body': prosemirror_body_string(u'Content'),
                'integer': 42,
                'email': '42@42.com',
                'char': 'New 42',
            }
        }
        response = self.client.put(self.api_edit_url, data=update_data, format='json')
        self.assertEqual(response.status_code, 200)

        # Two sessions after the edition
        self.assertEqual(2, sessions.count())

        latest_content = self.item.last_session

        self.assertIsNotNone(latest_content.content)
        self.assertEqual(latest_content.content['integer'], 42)
        self.assertEqual(latest_content.content['email'], '42@42.com')
        self.assertEqual(latest_content.content['char'], 'New 42')

    @skip("View obsoleted by the new Vue.js UI")
    def test_copy_to_general_type(self):
        item = items_factories.ConfirmedItemFactory.create(desk=self.desk)
        url = reverse('ui_item_copy', kwargs={
            'item_pk': item.pk,
            'new_item_type': initial_item_types.ARTICLE_TYPE})
        response = self.client.get(url)
        self.assertNotContains(response, 'name="integer"')

    @skip("View obsoleted by the new Vue.js UI")
    def test_copy_to_custom_type(self):
        url = reverse('ui_item_copy', kwargs={
            'item_pk': self.item.pk,
            'new_item_type': 'ctype-{0}'.format(self.item_type.pk)
        })
        response = self.client.get(url)
        self.assertContains(response, 'type="number" name="integer" value="42"')

        data = {
            'title': 'title',
            'publication_dt': '01/01/2015',
            'integer': 43,
            'email': '43@43.com',
            'char': '43'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        new_item = Item.objects.latest('created_at')
        self.assertRedirects(response, reverse('ui_item_details', args=[new_item.pk]))

        self.assertNotEqual(new_item.pk, self.item.pk)
        self.assertEqual(new_item.content['integer'], 43)

    @skip("View obsoleted by the new Vue.js UI")
    def test_change_item_type_to_general_type(self):
        url = reverse('ui_item_types_edit', kwargs={
            'item_pk': self.item.pk,
            'new_item_type': initial_item_types.ARTICLE_TYPE})
        response = self.client.get(url)
        self.assertNotContains(response, 'name="integer"')

    @skip("View obsoleted by the new Vue.js UI")
    def test_change_item_type_to_another_custom_type(self):
        new_content_schema = [
            {
                'type': item_content_fields.CHAR_TYPE,
                'name': 'char'
            },
            {
                'type': item_content_fields.CHAR_TYPE,
                'name': 'other_char'
            }
        ]

        new_custom_type = factories.ItemTypeFactory.create(
            desk=self.desk,
            content_schema=new_content_schema,
        )
        url = reverse('ui_item_types_edit', kwargs={
            'item_pk': self.item.pk,
            'new_item_type': 'ctype-{0}'.format(new_custom_type.pk)})

        data = {
            'title': 'title',
            'publication_dt': '01/01/2015',
            'char': '43',
            'other_char': '44'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        item = Item.objects.get(pk=self.item.pk)
        self.assertRedirects(response, reverse('ui_item_details', args=[item.pk]))

        self.assertEqual(item.content['char'], '43')
        self.assertEqual(item.content['other_char'], '44')


class HiddencontentCustomTypeTest(PilotEditorUserMixin, APITestCase):
    """Testing custom type with hidden content."""

    def setUp(self):
        activate('fr')
        super(HiddencontentCustomTypeTest, self).setUp()

        self.no_body_schema = [
            {
                'type': item_content_fields.CHAR_TYPE,
                'name': 'title',
                'label': "Titre",
                'required': False
            }
        ]
        self.item_type = factories.ItemTypeFactory.create(
            desk=self.desk,
            content_schema=self.no_body_schema
        )

    @skip("Test obsoleted by the new Vue.js UI")
    def test_item_add_form(self):
        """Custom type form is rendered in add item view."""
        url = reverse('ui_item_add_with_item_type', args=[self.item_type.technical_name])

        response = self.client.get(url)
        self.assertNotContains(response, 'name="body"')

        post_data = {
            'title': 'Title',
            'guidelines': 'Guidelines.',
            'publication_dt': datetime.datetime.today().strftime('%Y-%m-%d'),
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)

        item = Item.objects.get(guidelines=post_data['guidelines'])
        session = EditSession.objects.get(item=item)
        self.assertEqual(session.body, {})

    def test_item_edit_with_custom_type(self):
        """Submit form with correct custom type data."""

        item = items_factories.ItemFactory.create(
            desk=self.desk,
            channel=None,
            item_type=self.item_type
        )

        api_edit_url = reverse(API_ITEMS_DETAIL_URL, kwargs={'pk': item.pk})
        response = self.client.get(api_edit_url)
        self.assertNotIn('body', response.data['content'])

        update_data = {
            'content': {
                'title': 'Title'
            }
        }
        response = self.client.put(api_edit_url, data=update_data, format='json')
        self.assertEqual(response.status_code, 200)

        item = Item.objects.get(pk=item.pk)
        self.assertNotIn('body', item.content)

@skip("Tests obsoleted by the new Vue.js UI")
class ItemsCustomTypeUiTest(PilotAdminUserMixin, TestCase):
    """Test CRUD on ItemType objects."""

    def setUp(self):
        super(ItemsCustomTypeUiTest, self).setUp()

        # Keep a reference to the list view URL.
        self.custom_item_types_list_url = reverse('ui_item_types_list')

        self.item_type = factories.ItemTypeFactory.create(desk=self.desk)
        self.item_type_from_other_desk = factories.ItemTypeFactory.create()

    def test_list(self):
        """ Test item custom type list."""
        response = self.client.get(self.custom_item_types_list_url)
        self.assertEqual(response.status_code, 200)
        # View context must contain one and only one custom type created in setup.
        self.assertEqual(len(response.context['custom_types']), 1)

        # We delete it.
        self.item_type.delete()

        response = self.client.get(self.custom_item_types_list_url)
        self.assertEqual(response.status_code, 200)
        # The list must now be empty.
        self.assertEqual(len(response.context['custom_types']), 0)

    def test_create(self):
        """ Test item custom type creation."""

        url = reverse('ui_item_types_add')

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.

        post_data = {
            'name': u'Custom çontent typé',
            'description': u'Déscription',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.custom_item_types_list_url)

        response = self.client.get(reverse('ui_item_types_list'))
        # The list must contain the newly created custom type.
        self.assertEqual(len(response.context['custom_types']), 2)
        # The ItemType table must contain 2 elements.
        self.assertEqual(ItemType.objects.filter(desk=self.desk).count(), 2)

        # The page must contain the name in the list
        self.assertContains(response, post_data['name'], 1)

    def test_edit(self):
        """ Test item custom type edition."""

        url = reverse('ui_item_types_edit', args=[self.item_type.pk])

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        post_data = {
            'name': u'Updâted name',
            'description': u'Updated Descriptîon',
        }

        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.custom_item_types_list_url)

        # Check if object was updated.
        item = ItemType.objects.get(pk=self.item_type.pk)
        self.assertEqual(item.name, post_data['name'])
        self.assertEqual(item.description, post_data['description'])

    def test_edit_from_another_desk(self):
        """ Testing edition on an custom type from another desk. It should be forbidden."""
        url = reverse('ui_item_types_edit', args=[self.item_type_from_other_desk.pk])

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # Test POST.
        post_data = {
            'name': u'Updâted name',
            'description': u'Updated Descriptîon',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 404)

    def test_delete(self):
        """ Test item custom type deletion."""
        url = reverse('ui_item_types_delete', args=[self.item_type.pk])

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.custom_item_types_list_url)

        # Check if object was deleted.
        items = ItemType.objects.filter(pk=self.item_type.pk).count()
        self.assertEqual(items, 0)

    def test_delete_from_another_desk(self):
        """ Testing deletion on an custom type from another desk. It should be forbidden."""
        url = reverse('ui_item_types_delete', args=[self.item_type_from_other_desk.pk])

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # Test POST.

        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        # Check if object was deleted.
        items = ItemType.objects.filter(pk=self.item_type.pk).count()
        self.assertEqual(items, 1)
