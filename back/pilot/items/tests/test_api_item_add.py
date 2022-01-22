from unittest.case import skip

from django.urls import reverse
from rest_framework.test import APITestCase

from pilot.activity_stream.models import Activity
from pilot.items.tests.test_api import API_ITEMS_LIST_URL
from pilot.projects.tests import factories as projects_factories
from pilot.channels.tests import factories as channels_factories
from pilot.utils.prosemirror.prosemirror import EMPTY_PROSEMIRROR_DOC
from pilot.pilot_users.tests import factories as pilot_users_factories
from pilot.targets.tests import factories as targets_factories
from pilot.item_types.tests import factories as item_types_factories

from pilot.utils.test import PilotAdminUserMixin, prosemirror_body, ItemTypeTestingMixin


class ItemApiItemCreateTest(PilotAdminUserMixin, APITestCase, ItemTypeTestingMixin):

    def setUp(self):
        super(ItemApiItemCreateTest, self).setUp()
        self.url = reverse(API_ITEMS_LIST_URL)

    def test_create_default_item(self):
        post_data= {
            'item_type_id': self.get_item_type_article().id
        }
        self.check_create_item(post_data)
        self.assertEqual(u'', self.last_item.title)
        self.check_activity()
        self.check_snapshot(post_data)

    def test_create_tweet_item(self):
        my_body = prosemirror_body("mon text")
        post_data= {
            'item_type_id': self.get_item_type_twitter().id,
            'content': {'title': u'A title', 'body': my_body},
            'publication_date': u'2016-01-01',
            'publication_time': u'12:15',
            'addanother': 'true'
        }
        self.check_create_item(post_data)
        self.assertEqual(u'A title', self.last_item.title)
        self.assertEqual(my_body, self.last_item.content['body'])

    def test_create_tweet_item_with_unicode(self):
        my_body = prosemirror_body("Item content ünicôdé")
        post_data= {
            'item_type_id': self.get_item_type_twitter().id,
            'content': {'title': u'title ünicôdé', 'body': my_body},
            'publication_date': u'2016-01-01',
            'publication_time': u'12:15',
            'addanother': 'true'
        }
        self.check_create_item(post_data)
        self.assertEqual(u'title ünicôdé', self.last_item.title)
        self.assertEqual(my_body, self.last_item.content['body'])
        self.check_snapshot(post_data)

    def test_create_facebook_item(self):
        post_data= {
            'item_type_id': self.get_item_type_facebook().id,
            'content': {'title': u'A title'},
        }
        self.check_create_item(post_data)
        self.assertEqual(u'A title', self.last_item.title)

    def test_create_custom_item(self):
        item_type = item_types_factories.ItemTypeFactory.create(desk=self.desk)
        post_data = {
            'item_type_id': item_type.pk
        }
        self.check_create_item(post_data)
        self.assertEqual(item_type.id, self.last_item.item_type.id)

    @skip("Item Creation API cannot handle this anymore")
    def test_create_item_with_all_foreign_keys(self):
        other_user = pilot_users_factories.EditorFactory.create()
        channel = channels_factories.ChannelFactory.create(desk=self.desk)
        project = projects_factories.ProjectFactory.create(desk=self.desk)
        target1 = targets_factories.TargetFactory.create(desk=self.desk)
        target2 =  targets_factories.TargetFactory.create(desk=self.desk)
        api_item_create_url = self.url
        post_data= {
            'item_type': u'default',
            'owners': [u'%s' % self.user.pk, u'%s' % other_user.pk],
            'channel': u'%s' % channel.pk,
            'project': u'%s' % project.pk,
            'targets': [u'%s' % target1.pk, u'%s' % target2.pk]
        }
        response = self.client.post(api_item_create_url, post_data, format='json')
        self.assertEqual(201, response.status_code, response)
        self.last_item = Item.objects.last()
        self.assertEqual(2, self.last_item.owners.count())
        self.assertEqual(channel, self.last_item.channel)
        self.assertEqual(project, self.last_item.project)
        self.assertEqual(2, self.last_item.targets.count())

    def test_create_error_twitter_body_too_long(self):
        post_data= {
            'content': {'title': u'A title', 'body': prosemirror_body("x" * 300)},
            'item_type_id': self.get_item_type_twitter().id,
        }
        response = self.response(post_data)
        self.assertEqual(400, response.status_code, (response.status_code,response.content))

    def test_remove_content_not_in_schema(self):
        post_data= {
            'content': {'title': u'A title', 'not_in_schema': 'foo'},
            'item_type_id': self.get_item_type_facebook().id,
        }
        self.check_create_item(post_data)
        self.assertEqual(u'A title', self.last_item.title)
        self.assertEqual([u'title', u'body'], self.last_item.content.keys())

    def response(self, post_data):
        api_item_create_url = self.url
        return self.client.post(api_item_create_url, post_data, format='json')

    def check_create_item(self, post_data):
        response = self.response(post_data)
        self.assertEqual(201, response.status_code, response.content)
        self.last_item = Item.objects.last()
        self.assertEqual('Brouillon', self.last_item.workflow_state.label)
        self.assertEqual(post_data['item_type_id'], self.last_item.item_type.id)
        self.assertEqual(None, self.last_item.channel)
        self.assertEqual(None, self.last_item.project)
        self.assertEqual(0, self.last_item.owners.count())
        self.assertEqual(0, self.last_item.targets.count())

    def check_activity(self):
        activity_stream = Activity.activities_for(self.last_item)
        self.assertEqual(1, len(activity_stream))

    def check_snapshot(self, post_data):
        title = post_data['content']['title'] if ('content' in post_data) else ''
        body = post_data['content']['body'] if ('content' in post_data) else EMPTY_PROSEMIRROR_DOC
        session = EditSession.objects.get(item=self.last_item)
        self.assertEqual(session.title, title)
        self.assertEqual(session.content['body'], body)
        self.assertEqual(session.version, '1.0')
        self.assertEqual(session.created_by, self.last_item.created_by)
