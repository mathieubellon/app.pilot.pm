import json

from django.urls import reverse
from rest_framework.test import APITestCase

from pilot.items.tests.test_api import API_ITEMS_DETAIL_URL, API_ITEMS_LIST_URL
from pilot.projects.tests import factories as projects_factories
from pilot.channels.tests import factories as channels_factories
from pilot.items.tests import factories as items_factories
from pilot.utils.test import PilotRestrictedEditorUserMixin, prosemirror_body


class ItemsUiTestRestrictedEditorPermsTest(PilotRestrictedEditorUserMixin, APITestCase):
    """Test access perms for a `restricted editor` user."""

    def request_api(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return json.loads(response.content)

    def check_new_content(self, item):
        item_data = {
            'content':{
                'title': 'New version title',
                'body': prosemirror_body(u'New version content'),
            }
        }
        response = self.client.put(reverse(API_ITEMS_DETAIL_URL, kwargs={'pk': item.pk}), data=item_data, format='json')
        self.assertEqual(response.status_code, 200)

    def check_get_list(self, item):
        content = self.request_api(reverse(API_ITEMS_LIST_URL))
        self.assertEqual(1, content['count'])
        self.assertEqual(item.pk, content['objects'][0]['id'])

    def check_get_version(self, item):
        versions = self.request_api(reverse('api_item_versions_list', kwargs={'item_pk': item.pk}))
        self.assertEqual(1, len(versions))
        session = item.sessions.earliest()
        url = reverse('api_session', kwargs={'pk': session.pk, 'item_pk': item.pk})
        response = self.request_api(url)

    def check_diff(self, item):
        self.check_new_content(item)
        left = item.sessions.earliest()
        right = item.sessions.latest()
        url = reverse('api-items-diff/(?P<left-snapshot-pk>\d+)/(?P<right-snapshot-pk>\d+)',
                      kwargs={'pk': item.pk, 'left_snapshot_pk': left.pk, 'right_snapshot_pk': right.pk, })
        self.request_api(url)

    def check_snapshot(self, item):
        session = item.sessions.earliest()
        snapshot = self.request_api(reverse('api_session', kwargs={'pk': session.pk, 'item_pk': item.pk }))
        self.assertEqual('1.0', snapshot['version'])

    def check_review(self, item):
        self.request_api(reverse('api_item_sharings', kwargs={'item_pk': item.pk, }))

class CommonRestrictedTest(object):

    def test_get_list(self):
        self.check_get_list(self.item)

    def test_put(self):
        self.check_new_content(self.item)

    def test_version(self):
        self.check_get_version(self.item)

    def test_diff(self):
        self.check_diff(self.item)

    def test_snapshot(self):
        self.check_snapshot(self.item)

    def test_review(self):
        self.check_review(self.item)

    def test_allowed_views(self):
        allowed_views = ['ui_item_details']
        for view in allowed_views:
            url = reverse(view, kwargs={'item_pk': self.item.pk})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, 'error for view: {}'.format(view))

class ItemsUiTestRestrictedEditorPermsInProjectTest(ItemsUiTestRestrictedEditorPermsTest, CommonRestrictedTest):
    """Test access for  `restricted editor` user.
    Item created belong to project owned by user
    """

    def setUp(self):
        super(ItemsUiTestRestrictedEditorPermsInProjectTest, self).setUp()
        project = projects_factories.ProjectFactory.create(desk=self.desk)
        project.owners.add(self.restricted_user)

        self.item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk,
            project=project
        )


class ItemsUiTestRestrictedEditorPermsInChannelTest(ItemsUiTestRestrictedEditorPermsTest, CommonRestrictedTest):
    """Test access for  `restricted editor` user.
    Item created belong to channel owned by user
    """

    def setUp(self):
        super(ItemsUiTestRestrictedEditorPermsInChannelTest, self).setUp()

        channel = channels_factories.ChannelFactory.create(desk=self.desk)
        channel.owners.add(self.restricted_user)

        self.item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk,
            channel=channel
        )

class ItemsUiTestRestrictedEditorPermsCreatedByTest(ItemsUiTestRestrictedEditorPermsTest, CommonRestrictedTest):
    """Test access for  `restricted editor` user.
    Item is created by user
    """

    def setUp(self):
        super(ItemsUiTestRestrictedEditorPermsCreatedByTest, self).setUp()
        self.item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk,
            created_by=self.restricted_user
        )

class ItemsUiTestRestrictedEditorPermsDefaultTest(ItemsUiTestRestrictedEditorPermsTest):

    def setUp(self):
        super(ItemsUiTestRestrictedEditorPermsDefaultTest, self).setUp()
        self.item =  items_factories.ConfirmedItemFactory.create(desk=self.desk)

    def test_get_list(self):
        response = self.client.get(reverse(API_ITEMS_LIST_URL), format='json')
        content = json.loads(response.content)
        self.assertEqual(0, content['count'])
        self.client.logout()
        self.client.login(email=self.user.email, password='password')
        self.check_get_list(self.item)

    def test_put(self):
        response = self.client.put(reverse(API_ITEMS_DETAIL_URL, kwargs={'pk': self.item.pk}), data={}, format='json')
        self.assertEqual(response.status_code, 404)
        self.client.logout()
        self.client.login(email=self.user.email, password='password')
        self.check_new_content(self.item)

    def test_version(self):
        response = self.client.put(reverse('api_item_versions_list', kwargs={'item_pk': self.item.pk}))
        self.assertEqual(response.status_code, 405)
        self.client.logout()
        self.client.login(email=self.user.email, password='password')
        self.check_get_version(self.item)

    def test_snapshot(self):
        session = self.item.sessions.earliest()
        response = self.client.put(reverse('api_session', kwargs={'pk': session.pk,
                                                                        'item_pk': self.item.pk }))
        self.assertEqual(response.status_code, 405)
        self.client.logout()
        self.client.login(email=self.user.email, password='password')
        self.check_snapshot(self.item)

    def test_allowed_views(self):
        response = self.client.get(reverse('ui_items_list'))
        self.assertEqual(response.status_code, 200)

    def test_unallowed_views(self):
        unallowed_views = [
            'ui_item_details']
        for view in unallowed_views:
            url = reverse(view, kwargs={'item_pk': self.item.pk})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
