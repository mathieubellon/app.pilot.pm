from unittest import skip

from django.urls import reverse
from django.test import TestCase

from pilot.items.tests import factories as items_factories
from pilot.utils import pilot_languages
from pilot.utils.test import PilotAdminUserMixin


class ItemReviewsUiTest(PilotAdminUserMixin, TestCase):

    def setUp(self):
        super(ItemReviewsUiTest, self).setUp()

    def test_item_sharing_can_be_edited(self):
        """Test the item review EDIT process."""
        self.check_page(is_editable=True)

    def test_item_sharing_can_not_be_edited(self):
        """Test the item review Not EDIT process."""
        self.check_page(is_editable=False)

    def test_item_sharing_language(self):
        """ Test the language switch in the item review process because it's a different mechanism from other pages """
        response = self.check_page(is_editable=False)
        self.assertEqual(self.review.session.item.desk.language, pilot_languages.FR_LANG)
        self.assertContains(response, 'lang="{0}"'.format(pilot_languages.FR_LANG))
        self.assertEqual(response.context['LANGUAGE_CODE'], pilot_languages.FR_LANG)

        self.desk.language = pilot_languages.EN_LANG
        self.desk.save()
        self.assertEqual(self.review.session.item.desk.language, pilot_languages.EN_LANG)  # Sanity check
        response = self.client.get(self.url)
        self.assertContains(response, 'lang="{0}"'.format(pilot_languages.EN_LANG))  # Check html lang
        self.assertEqual(response.context['LANGUAGE_CODE'], pilot_languages.EN_LANG)

    def check_page(self, is_editable):
        item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk
        )
        snapshot = items_factories.EditSessionFactory.create(item=item)
        self.review = items_factories.ReviewFactory(session=snapshot, is_editable=is_editable)

        self.url = reverse('ui_item_sharing', kwargs={'review_pk': self.review.pk, 'token': self.review.token})
        response = self.client.get(self.url)

        return response

class ItemReviewsUIPasswordTest(PilotAdminUserMixin, TestCase):

    def setUp(self):
        super(ItemReviewsUIPasswordTest, self).setUp()
        item = items_factories.ItemFactory.create()
        snapshot = items_factories.EditSessionFactory.create(item=item)
        review = items_factories.ReviewFactory(session = snapshot, password=u'1234')
        self.url = reverse('ui_item_sharing_password_required',
                           kwargs={'review_pk': review.pk, 'token': review.token, })
        self.url_redirect =  reverse('ui_item_sharing',
                                     kwargs={'review_pk': review.pk, 'token': review.token})

    def test_correct_password(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        post_data = { 'password': '1234' }
        response = self.client.post(self.url, data=post_data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(self.url_redirect, response['Location'])

    def test_not_correct_password(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        post_data = { 'password': 'pass' }
        response = self.client.post(self.url, data=post_data)
        self.assertEqual(200, response.status_code)
        exepected_error = u'Mot de passe incorrect. Merci de noter que les mots de passe sont sensibles à la casse.'
        self.assertFormError(response, 'form', 'password', exepected_error)
