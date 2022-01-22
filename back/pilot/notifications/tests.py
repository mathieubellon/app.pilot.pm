from unittest.case import skip

from django.core import mail
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APITestCase

from pilot.desks.tests import factories as desks_factories
from pilot.items.tests import factories as items_factories
from pilot.items.tests.test_api import API_ITEMS_DETAIL_URL
from pilot.notifications import factories as notification_factories
from pilot.pilot_users.tests import factories as user_factories
from pilot.utils.test import PilotAdminUserMixin, WorkflowStateTestingMixin


class FactoriesTests(TestCase):
    def test_notification_factories(self):
        notification = notification_factories.NotificationFactory()
        self.assertIsNotNone(notification.send_by)
        self.assertIsNotNone(notification.to)
        self.assertIsNotNone(notification.send_at)
        self.assertFalse(notification.is_read)
        self.assertEqual(
            notification.get_absolute_url(),
            u'/notifications/goto/{0}'.format(notification.id)
        )

    def test_onitemcommentnotification_factories(self):
        notification = notification_factories.OnItemCommentNotificationFactory()
        self.assertIsNotNone(notification.send_by)
        self.assertIsNotNone(notification.to)
        self.assertIsNotNone(notification.send_at)
        self.assertFalse(notification.is_read)
        self.assertEqual(
            notification.get_target_url(),
            u'/items/{0}/?scrollto=comment-{1}'.format(notification.on.pk, notification.comment_id)
        )

    def test_onitemannotationnotification_factories(self):
        notification = notification_factories.OnItemAnnotationNotificationFactory()
        self.assertIsNotNone(notification.send_by)
        self.assertIsNotNone(notification.to)
        self.assertIsNotNone(notification.send_at)
        self.assertFalse(notification.is_read)
        self.assertEqual(
            notification.get_target_url(),
            u'/items/{0}/?scrollto=annotation-{1}'.format(notification.on.pk, notification.annotation_uuid)
        )

    def test_onitemideanotification_factories(self):
        notification = notification_factories.OnItemIdeaNotificationFactory()
        self.assertEqual(
            notification.get_target_url(),
            u'/items/{0}/?scrollto=comment-{1}'.format(notification.on.pk, notification.comment_id)
        )

    def test_onprojectnotification_factories(self):
        notification = notification_factories.OnProjectNotificationFactory()
        self.assertIsNotNone(notification.send_by)
        self.assertIsNotNone(notification.to)
        self.assertIsNotNone(notification.send_at)
        self.assertFalse(notification.is_read)
        self.assertEqual(
            notification.get_target_url(),
            u'/projects/{0}/#comment-{1}'.format(notification.on.pk, notification.comment_id)
        )

    def test_onprojectideanotification_factories(self):
        notification = notification_factories.OnProjectIdeaNotificationFactory()
        self.assertEqual(
            notification.get_target_url(),
            u'/projects/{0}/#comment-{1}'.format(notification.on.pk, notification.comment_id)
        )


class NotificationsTest(PilotAdminUserMixin, WorkflowStateTestingMixin, APITestCase):
    @skip('Must be rewritten against the new Comment API')
    def test_notify_when_mentionned_in_comment(self):
        """the `notify_when_mentionned_in_comment()` function is triggered
        with a signal when a comment is posted"""

        to_user = user_factories.PilotUserFactory()

        self.assertTrue(to_user.mention_by_email)  # Ensuring to_user agrees to receive notification emails
        to_user.organizations.add(self.organization)
        to_user.desks.add(self.desk)

        other_organization_user = user_factories.PilotUserFactory()

        other_desk = desks_factories.DeskFactory.create()
        other_desk_user = user_factories.PilotUserFactory()
        other_desk_user.organizations.add(self.organization)
        other_desk_user.desks.add(other_desk)

        item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk,
            workflow_state=self.get_state_edition_ready()
        )

        # Refresh the cached item instance to ensure to fetch the RelatedFactory results (i.e. the EditSession obj).
        url = reverse('ui_ajax_item_comment_post', kwargs={'item_pk': item.pk})

        # POST of a comment with a comment mentionning an inexistant user.
        post_data = {'comment': 'Comment mentîonning @azertyû', }
        self.client.post(url, data=post_data)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Notification.objects.count(), 0)

        # POST of a comment mentionning an user from another organization.
        post_data = {'comment': 'Comment mentîonning @{0}'.format(other_organization_user.username), }
        self.client.post(url, data=post_data)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Notification.objects.count(), 0)

        # POST of a comment mentionning an user from another desk.
        post_data = {'comment': 'Comment mentîonning @{0}'.format(other_desk_user.username), }
        self.client.post(url, data=post_data)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Notification.objects.count(), 0)

        # POST of a comment with a correct mention.
        post_data = {'comment': 'Comment mentîonning @{0}'.format(to_user.username), }
        self.client.post(url, data=post_data)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(mail.outbox[0].to, [to_user.email])
        self.assertIn("[Pilot] [mention]", mail.outbox[0].subject)
        self.assertIn("Contenu #%s" % item.pk, mail.outbox[0].subject)
        self.assertIn(item.__str__(), mail.outbox[0].subject)

    def test_notify_when_mentionned_in_annotation(self):
        """the `notify_when_mentionned_in_annotation()` function is called when a annotation is posted"""

        sender = user_factories.PilotUserFactory()
        sender.organizations.add(self.organization)
        sender.desks = [self.desk]

        other_desk_user = user_factories.PilotUserFactory()
        other_desk = desks_factories.DeskFactory(organization=self.organization, created_by=other_desk_user)
        other_desk_user.organizations.add(self.organization)
        other_desk_user.desks = [other_desk]

        self.assertEqual(sender.organizations.all()[0], other_desk_user.organizations.all()[0])
        self.assertNotEqual(sender.desks.all()[0], other_desk_user.desks.all()[0])

        to_user, to_user_2, to_user_3 = user_factories.PilotUserFactory.create_batch(3)
        for user in to_user, to_user_2, to_user_3:
            self.assertTrue(user.mention_by_email)  # Ensuring to_user agrees to receive notification emails
            user.organizations.add(self.organization)
            user.desks.add(self.desk)

        other_organization_user = user_factories.PilotUserFactory()
        item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk,
            workflow_state=self.get_state_edition_ready()
        )

        url = reverse(API_ITEMS_DETAIL_URL, kwargs={'pk': item.pk})

        # POST of a comment with a comment mentionning an inexistant user.
        json_sender = {
            "id": sender.pk,
            "username": sender.username,
            "avatar": "http://domain.com/avatar.png"
        }
        annotation = {
            "id": "123",
            "mainComment": {
                "date": "2016-07-01T14:36:04.702Z",
                "text": "Comment mentîonning @xyz",  # inexistant user
                "user": json_sender
            },
            "comments": [],
            "resolved": False,
            "resolvedBy": None,
            "range": {
                "from": 20,
                "to": 25
            },
            "selectedText": "meh!!"
        }

        json_item = {
            'annotations': {
                'body': {
                    '123': annotation
                }
            }
        }

        self.client.put(url, data=json_item, format='json')
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Notification.objects.count(), 0)

        # POST of a comment with a correct mention of a user from another desk.
        annotation['mainComment']['content'] = 'Comment mentîonning @{0}'.format(other_desk_user.username)
        self.client.put(url, data=json_item, format='json')
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Notification.objects.count(), 0)

        # POST of a comment with a correct mention of a user from another organization.
        annotation['mainComment']['content'] = 'Comment mentîonning @{0}'.format(other_organization_user.username)
        self.client.put(url, data=json_item, format='json')
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Notification.objects.count(), 0)

        # POST of a comment with a correct mention.
        annotation['mainComment']['content'] = 'Comment mentîonning @{0}'.format(to_user.username)
        self.client.put(url, data=json_item, format='json')
        self.assertEqual(Notification.objects.count(), 1)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [to_user.email])
        self.assertIn("[Pilot] [mention]", mail.outbox[0].subject)
        self.assertIn("Contenu #%s" % item.pk, mail.outbox[0].subject)
        self.assertIn(item.__str__(), mail.outbox[0].subject)

        # Edit the comment with a new @mention also trigger notifications
        annotation['mainComment']['content'] = 'Comment mentîonning @{0} and @{1}'.format(
            to_user.username,
            to_user_2.username)
        self.client.put(url, data=json_item, format='json')
        self.assertEqual(Notification.objects.count(), 2)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].to, [to_user_2.email])
        self.assertIn("[Pilot] [mention]", mail.outbox[1].subject)
        self.assertIn("Contenu #%s" % item.pk, mail.outbox[1].subject)
        self.assertIn(item.__str__(), mail.outbox[1].subject)

        # Post of a non-main comment also trigger notifications
        annotation['comments'].append({
            "date": "2016-07-01T14:37:04.702Z",
            "text": "Comment mentîonning @{0}".format(to_user_3.username),
            "user": json_sender
        })
        self.client.put(url, data=json_item, format='json')
        self.assertEqual(Notification.objects.count(), 3)

        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(mail.outbox[2].to, [to_user_3.email])
        self.assertIn("[Pilot] [mention]", mail.outbox[2].subject)
        self.assertIn("Contenu #%s" % item.pk, mail.outbox[2].subject)
        self.assertIn(item.__str__(), mail.outbox[2].subject)

    def test_delete_notification_when_mention_disappear(self):

        sender = user_factories.PilotUserFactory()
        sender.organizations.add(self.organization)
        sender.desks.add(self.desk)

        to_user, to_user_2, to_user_3 = user_factories.PilotUserFactory.create_batch(3)
        for user in to_user, to_user_2, to_user_3:
            self.assertTrue(user.mention_by_email)  # Ensuring to_user agrees to receive notification emails
            user.organizations.add(self.organization)
            user.desks.add(self.desk)

        item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk,
            workflow_state=self.get_state_edition_ready()
        )

        url = reverse(API_ITEMS_DETAIL_URL, kwargs={'pk': item.pk})

        json_sender = {
            "id": sender.pk,
            "username": sender.username,
            "avatar": "http://domain.com/avatar.png"
        }
        annotation = {
            "id": "123",
            "mainComment": {
                "date": "2016-07-01T14:36:04.702Z",
                "text": "Comment mentîonning @{0} and @{1}".format(
                    to_user.username,
                    to_user_2.username),
                "user": json_sender
            },
            "comments": [{
                "date": "2016-07-01T14:37:04.702Z",
                "text": "Comment mentîonning @{0}".format(to_user_3.username),
                "user": json_sender
            }],
            "resolved": False,
            "resolvedBy": None,
            "range": {
                "from": 20,
                "to": 25
            },
            "selectedText": "meh!!"
        }
        json_item = {
            'annotations': {
                'body': {
                    '123': annotation
                }
            }
        }

        self.client.put(url, data=json_item, format='json')
        self.assertEqual(Notification.objects.count(), 3)

        # Editing the comment while removing an @mention should delete the corresponding notification
        annotation['mainComment']['content'] = 'Comment mentîonning @{0}'.format(to_user.username)
        self.client.put(url, data=json_item, format='json')
        self.assertEqual(Notification.objects.count(), 2)

        # Removing a comment where there was an @mention should delete the corresponding notification
        annotation['comments'] = []
        self.client.put(url, data=json_item, format='json')
        self.assertEqual(Notification.objects.count(), 1)

        # Removing the whole annotation should also remove the notification
        json_item = {
            'annotations': {}
        }
        self.client.put(url, data=json_item, format='json')
        self.assertEqual(Notification.objects.count(), 0)
