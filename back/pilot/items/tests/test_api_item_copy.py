from unittest.case import skip

from django.utils.encoding import force_str
from django.urls import reverse
from rest_framework.test import APITestCase

from pilot.items.tests import factories as items_factories
from pilot.item_types import initial_item_types
from pilot.utils.test import PilotAdminUserMixin
from pilot.item_types.tests import factories as item_types_factories

class ItemApiItemCopyTest(PilotAdminUserMixin, APITestCase):

    @skip("View obsoleted by the new Vue.js UI")
    def test_item_copy_destination_type_choice(self):
        ct_list = item_types_factories.ItemTypeFactory.create_batch(3, desk=self.desk)

        item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk
        )

        url_copy = reverse('ui_item_copy_choice', args=[item.pk])
        url_edit = reverse('ui_it_edit_choice', args=[item.pk])

        # Checking the generated choice field for editing
        response = self.client.get(url_edit)
        self.assertEqual(response.status_code, 200)
        choices = response.context['form'].fields['new_item_type'].choices
        # When editing, the current item type should not appear in the choices lists
        self.assertFalse(force_str(item.item_type.name) in [s[1] for s in choices])
        self.assertEqual(len(choices), 5)

        # Test Post

        # Copy item with hardcoded item type
        post_data = {'new_item_type': initial_item_types.ARTICLE_TYPE}
        response = self.client.post(url_copy, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_item_copy', kwargs={'item_pk': item.pk,
                                                                       'new_item_type': initial_item_types.ARTICLE_TYPE}))

        # Edit item with hardcoded item type
        post_data = {'new_item_type': initial_item_types.TWITTER_TYPE}
        response = self.client.post(url_edit, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_item_types_edit', kwargs={'item_pk': item.pk,
                                                                            'new_item_type': initial_item_types.TWITTER_TYPE}))

        # Copy item with custom item type
        ct_utl_param = 'ctype-{0}'.format(ct_list[0].pk)
        post_data = {'new_item_type': ct_utl_param}
        response = self.client.post(url_copy, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('ui_item_copy', kwargs={'item_pk': item.pk, 'new_item_type': ct_utl_param})
        )

        # Edit item with custom item type
        ct_utl_param = 'ctype-{0}'.format(ct_list[1].pk)
        post_data = {'new_item_type': ct_utl_param}
        response = self.client.post(url_edit, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('ui_item_types_edit', kwargs={'item_pk': item.pk, 'new_item_type': ct_utl_param})
        )
