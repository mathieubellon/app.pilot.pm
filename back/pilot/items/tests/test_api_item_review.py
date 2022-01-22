import json

from unittest.case import skip

from django.core import mail
from django.urls import reverse
from django.conf import settings

from rest_framework.test import APITestCase

from pilot.utils.test import PilotAdminUserMixin
from pilot.items.tests import factories as items_factories
from pilot.items.models import Review
from pilot.pilot_users.tests import factories as users_factories
from pilot.utils.url import get_fully_qualified_url

REVIEW_LIST_FIELD = (
    'absolute_url',
    'comment',
    'created_at',
    'email',
    'has_fork',
    'id',
    'is_editable',
    'is_merged',
    'item_version',
    'reviewed_at',
    'review_comment',
    'status',
)


class GetReviewListTest(PilotAdminUserMixin, APITestCase):

    def setUp(self):
        super(GetReviewListTest, self).setUp()
        self.item = items_factories.ItemFactory.create()
        for _ in range(3):
            snapshot = items_factories.EditSessionFactory.create(item=self.item)
            items_factories.ReviewFactory(session = snapshot)
        self.url = reverse('api_item_sharings', args=[self.item.pk])

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, (response.status_code, response.content))
        reviews = json.loads(response.content)
        self.assertEqual(3, len(reviews), reviews)
        [self.assertTrue(key in reviews[0].keys(), (key, reviews[0])) for key in REVIEW_LIST_FIELD]


class CreateReviewTest(PilotAdminUserMixin, APITestCase):

    def setUp(self):
        super(CreateReviewTest, self).setUp()
        self.item = items_factories.ItemFactory.create()
        self.session = items_factories.EditSessionFactory.create(item=self.item)
        self.url = reverse('api_item_sharings', args=[self.item.pk])

    def test_create_review(self):
        email = 'VALIDATOR@VALIDATOR.ORG'
        post_data = {
            'email': email,
            'session': self.session.pk
        }
        json_response = self.create_review(post_data)

        self.assertEqual(email, json_response['email'])
        self.assertEqual(email, self.review.email)
        self.assertFalse(self.review.is_editable)
        self.assertEqual(Review.STATUS_PENDING, self.review.status)

        review = self.item.sessions.latest().reviews.all().get()
        # Ensure that the email is in lower case (EmailLowerCaseField should be used in the Form).
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(review.email, post_data['email'])
        self.assertEqual(review.status, Review.STATUS_PENDING)

    def test_create_review_with_error(self):
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, 400, (response.status_code, response.content))

        json_response = json.loads(response.content)
        self.assertTrue("Ce champ est obligatoire." in json_response['email'])

    def test_create_review_with_all_params(self):
        email = 'VALIDATOR@VALIDATOR.ORG'
        post_data = {
            'email': email,
            'session': self.session.pk,
            'is_editable': True,
            'comment': 'My comment',
            'password': '1234'
        }
        self.create_review(post_data)

        self.assertEqual('My comment', self.review.comment)
        self.assertTrue(self.review.is_editable)
        self.assertEqual('1234', self.review.password)

    def create_review(self, post_data):
        response = self.client.post(self.url, data=post_data)
        self.assertEqual(response.status_code, 201, (response.status_code, response.content))
        self.review = self.item.sessions.latest().reviews.all().get()
        return json.loads(response.content)


class GetReviewTest(PilotAdminUserMixin, APITestCase):

    def setUp(self):
        super(GetReviewTest, self).setUp()
        self.item = items_factories.ItemFactory.create()
        self.session = items_factories.EditSessionFactory.create(item=self.item)
        self.review = items_factories.ReviewFactory(session = self.session)

    @skip("Test obsoleted by the new Vue.js UI")
    def test_get_editable_review(self):
        url = reverse('ui_item_sharing', kwargs={'review_pk': self.review.pk, 'token': self.review.token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, (response.status_code, response.content))
        self.assertContains(response, 'Vous pouvez modifier ce document')
        self.assertContains(response, 'Valider')
        self.assertContains(response, 'Ne pas valider')


class BaseUpdateReviewTest(PilotAdminUserMixin, APITestCase):
    def setUp(self):
        super(BaseUpdateReviewTest, self).setUp()
        self.item = items_factories.ItemFactory.create()
        self.session = items_factories.EditSessionFactory.create(item=self.item)


class UpdateReviewTest(BaseUpdateReviewTest):
    def setUp(self):
        super(UpdateReviewTest, self).setUp()
        self.review = items_factories.ReviewFactory(session = self.session)
        self.url = reverse('api_sharing_external_item', kwargs={'pk': self.review.pk, 'token': self.review.token, 'item_pk': self.item.pk})

    def test_update_with_no_status(self):
        post_data = {
            'comment': u'Cômment',
         }
        response = self.client.put(self.url, data=post_data, format='json')
        self.assertEqual(response.status_code, 200, (response.status_code, response.content))
        review = self.item.sessions.latest().reviews.all().get()
        self.assertEqual(review.status, Review.STATUS_PENDING)
        self.assertEqual(review.comment, post_data['comment'])

        self.assertEqual(len(mail.outbox), 0)

    def test_approved(self):
        post_data = {
            'status': 'approved',
        }
        response = self.client.put(self.url, data=post_data, format='json')
        self.assertEqual(response.status_code, 200, (response.status_code, response.content))
        review = self.item.sessions.latest().reviews.all().get()
        self.assertEqual(review.status, Review.STATUS_APPROVED)

        self.assertEqual(len(mail.outbox), 1)
        message = users_messages.PilotMessage(
            mail_subject=users_messages.REVIEW_VERDICT_COMMON_SUBJECT_APPROVED,
            mail_body=''
        )
        outbox = mail.outbox[0]
        self.assertEqual(message.mail_subject, outbox.subject)
        self.assertIn('[Pilot] ', outbox.subject)
        self.assertIn(review.created_by.email, outbox.to)
        self.assertIn(review.email, outbox.body)
        self.assertIn(review.review_comment, outbox.body)
        self.assertIn(get_fully_qualified_url(review.session.item.get_absolute_url()), outbox.body)

    def test_not_approved(self):
        post_data = {
            'status': 'rejected'
        }
        response = self.client.put(self.url, data=post_data, format='json')
        self.assertEqual(response.status_code, 200, (response.status_code, response.content))
        review = self.item.sessions.latest().reviews.all().get()
        self.assertEqual(review.status, Review.STATUS_REJECTED)

        self.assertEqual(len(mail.outbox), 1)
        message = users_messages.PilotMessage(
            mail_subject=users_messages.REVIEW_VERDICT_COMMON_SUBJECT_REJECTED,
            mail_body=''
        )
        outbox = mail.outbox[0]
        self.assertEqual(message.mail_subject, outbox.subject)
        self.assertIn('[Pilot] ', outbox.subject)
        self.assertIn(review.created_by.email, outbox.to)
        self.assertIn(review.email, outbox.body)
        self.assertIn(review.review_comment, outbox.body)
        self.assertIn(get_fully_qualified_url(review.session.item.get_absolute_url()), outbox.body)


class ExternalUpdateReviewTest(BaseUpdateReviewTest):
    def setUp(self):
        super(ExternalUpdateReviewTest, self).setUp()
        self.review = items_factories.ReviewFactory(session = self.session)
        self.url = reverse('api_review_external_item', kwargs={'pk': self.review.pk, 'token': self.review.token, 'item_pk': self.item.pk})

        # Make the test with an anonymous user
        self.client.logout()


class InternalUpdateReviewTest(BaseUpdateReviewTest):

    def setUp(self):
        super(InternalUpdateReviewTest, self).setUp()
        self.other_user = users_factories.PilotUserFactory()
        self.review = items_factories.ReviewFactory(session = self.session, email=self.other_user.email)
        self.url = reverse('api_review_internal_item', kwargs={'pk': self.review.pk, 'item_pk': self.item.pk})

    def test_auth_is_required(self):
        self.client.logout()
        response = self.client.put(self.url, data={})
        self.assertEqual(response.status_code, 403)

