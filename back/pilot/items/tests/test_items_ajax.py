import json
from unittest import skip

from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from django.utils.dateformat import format as date_format
from django.utils import timezone

import django_comments
import mock

from pilot.items.tests import factories as items_factories
from pilot.pilot_users.tests import factories as user_factories
from pilot.utils.test import PilotAdminUserMixin


class ItemsUiTest(PilotAdminUserMixin, TestCase):
    """Test CRUD on Item objects."""

    def setUp(self):
        super(ItemsUiTest, self).setUp()
        super(ItemsUiTest, self).setUp()
        # Keep a reference to the list view URL.
        self.main_items_list_url = reverse('ui_items_list')
        self.scope_choices = (list(zip(*Item.SCOPE_CHOICES)) + [None])[0]

    def tearDown(self):
        # Delete all Item objects after each test.
        Item.objects.all().delete()

    @skip("Social features disabled for now")
    def test_ajax_tweet_item_publish_button_and_form(self):
        tweet_item = items_factories.ConfirmedItemTweetFactory.create(
            desk=self.desk
        )
        button_url = reverse('ui_ajax_item_publish_button', args=[tweet_item.pk])
        form_url = reverse('ui_ajax_item_publish_form', args=[tweet_item.pk])

        with mock.patch(
                'pilot.items.models.Item.can_publish_now',
                new_callable=mock.PropertyMock
        ) as mock_is_publishable, mock.patch(
            'pilot.items.models.Item.get_instant_publication_warnings',
            new_callable=mock.PropertyMock
        ) as mock_get_instant_publication_warnings:
            # Item is not publishable now
            mock_is_publishable.return_value = False
            response = self.client.get(button_url)
            self.assertNotContains(response, '#instant_publication_modal')
            self.assertContains(response, 'btn-fail')
            response = self.client.get(form_url)
            self.assertNotContains(response, '/tweet-publish/')
            self.assertNotContains(response, '/facebook-publish/')

            # Item is publishable now but raises warnings
            mock_is_publishable.return_value = True
            response = self.client.get(button_url)
            self.assertNotContains(response, 'data-target="#instant_publication_modal"')
            self.assertContains(response, 'btn-fail')

            # Item is publishable now and doesn't raise warning
            mock_get_instant_publication_warnings.return_value = []
            response = self.client.get(button_url)
            self.assertContains(response, 'data-target="#instant_publication_modal"')
            self.assertNotContains(response, 'btn-fail')
            response = self.client.get(form_url)
            self.assertNotContains(response, '/facebook-publish/')
            self.assertContains(response, '/tweet-publish/')

    @skip("Social features disabled for now")
    def test_ajax_facebook_item_publish_button_and_form(self):
        fb_item = items_factories.ItemFacebookFactory.create(
            desk=self.desk
        )
        button_url = reverse('ui_ajax_item_publish_button', args=[fb_item.pk])
        form_url = reverse('ui_ajax_item_publish_form', args=[fb_item.pk])

        # We need to patch item methods to fake publishable status
        with mock.patch(
                'pilot.items.models.Item.can_publish_now',
                new_callable=mock.PropertyMock
        ) as mock_is_publishable, mock.patch(
            'pilot.items.models.Item.get_instant_publication_warnings',
            new_callable=mock.PropertyMock
        ) as mock_get_instant_publication_warnings:
            # Item is not publishable now
            mock_is_publishable.return_value = False
            response = self.client.get(button_url)
            self.assertNotContains(response, 'data-target="#instant_publication_modal"')
            self.assertContains(response, 'btn-fail')

            response = self.client.get(form_url)
            self.assertNotContains(response, '/tweet-publish/')
            self.assertNotContains(response, '/facebook-publish/')

            # Item is publishable now but raises warnings
            mock_is_publishable.return_value = True
            response = self.client.get(button_url)
            self.assertNotContains(response, 'data-target="#instant_publication_modal"')
            self.assertContains(response, 'btn-fail')

            # Item is publishable now and doesn't raise warnings
            mock_is_publishable.return_value = True
            mock_get_instant_publication_warnings.return_value = []
            response = self.client.get(button_url)

            self.assertContains(response, 'data-target="#instant_publication_modal"')
            response = self.client.get(form_url)
            self.assertContains(response, '/facebook-publish/')
            self.assertNotContains(response, '/tweet-publish/')
            self.assertNotContains(response, 'btn-fail')

    @skip("Comments has been migrated to a dedicated API")
    def test_ajax_item_comments_annotations_list(self):
        """Test the comments attached to EditSession objects."""
        user_factories.PilotUserFactory.create()
        item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk
        )
        session = EditSession.objects.get(item=item)

        comment = django_comments.get_model()()
        comment.user = self.user
        comment.comment = "é!comment"
        comment.content_type = ContentType.objects.get_for_model(EditSession)
        comment.site = Site.objects.all()[0]
        comment.object_pk = item.EditSession.latest().pk
        comment.save()

        comment2 = django_comments.get_model()()
        comment2.user = self.user
        comment2.comment = "é!comment agaaaain"
        comment2.content_type = ContentType.objects.get_for_model(EditSession)
        comment2.site = Site.objects.all()[0]
        comment2.object_pk = item.EditSession.latest().pk
        comment2.save()

        url = reverse('ui_ajax_item_comments_annotations_list', kwargs={'session_pk': session.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)

        self.assertEqual(len(json_response), 2)
        # Comments and annotations are merged and listed in reverse chronologic order
        # so the first must be the last posted
        self.assertEqual(json_response[0]['comment_type'], 'comment')
        self.assertEqual(json_response[0]['username'], self.user.username)
        self.assertEqual(json_response[0]['comment'], comment2.comment)

        self.assertEqual(json_response[1]['comment_type'], 'comment')
        self.assertEqual(json_response[1]['username'], self.user.username)
        self.assertEqual(json_response[1]['comment'], comment.comment)

    @skip("Comments has been migrated to a dedicated API")
    def test_ajax_item_comment_post(self):
        """Test the comments attached to EditSession objects."""

        item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk
        )
        # Refresh the cached item instance to ensure to fetch the RelatedFactory results (i.e. the EditSession obj).
        item = Item.objects.get(pk=item.pk)
        url = reverse('ui_ajax_item_comment_post', kwargs={'item_pk': item.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)  # POST only view

        # Test POST of a comment.
        post_data = {
            'comment': 'Comment âttached to the latest EditSession object',
        }
        response = self.client.post(url, data=post_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'result': 'ok'})

        comment = django_comments.models.Comment.objects.get(object_pk=item.last_session.pk)
        self.assertEqual(comment.comment, post_data['comment'])
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.content_object, item.EditSession.latest())

        # Test empty POST of a comment.
        response = self.client.post(url, data={})
        self.assertEqual(json.loads(response.content)['result'], 'error')
