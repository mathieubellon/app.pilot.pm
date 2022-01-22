import datetime
import json

from django.urls import reverse
from django.db.models import Min, Max
from django.utils import timezone
from django.utils.timezone import make_naive
from rest_framework.test import APITestCase

from pilot.projects.tests import factories as projects_factories
from pilot.channels.tests import factories as channels_factories
from pilot.desks.tests import factories as desks_factories
from pilot.desks.models import Desk
from pilot.item_types.tests import factories as item_types_factories
from pilot.items.tests import factories as items_factories
from pilot.pilot_users.tests import factories as pilot_users_factories
from pilot.targets.tests import factories as targets_factories
from pilot.utils.test import PilotAdminUserMixin, PilotRestrictedEditorUserMixin, \
    WorkflowStateTestingMixin, ItemTypeTestingMixin
from pilot.activity_stream.models import Activity
from pilot.item_types.tests.testing_item_type_definition import SIMPLE_TEST_SCHEMA


API_ITEMS_DETAIL_URL = 'api-items-detail'
API_ITEMS_LIST_URL = 'api-items-list'

class ItemAPIMixin(object):
    ITEM_API_READ_ONLY_FIELDS = (
        'assets',
        'channel',
        'created_at',
        'created_by',
        'created_by_external_email',
        'id',
        'item_type',
        'last_session_id',
        'owners',
        'project',
        'scope',
        'targets',
        'tasks',
        'updated_at',
        'url',
        'version',
        'workflow_state',
    )
    ITEM_API_UPDATABLE_FIELDS = (
        'annotations',
        'available_pictures',
        'channels_id',
        'contacts',
        'content',
        'goal',
        'guidelines',
        'idea_state',
        'investigations_needed',
        'is_private',
        'language',
        'mappings',
        'owners_id',
        'photographer_needed',
        'photo_investigations_needed',
        'project_id',
        'publication_dt',
        'sources',
        'support_needed',
        'targets_id',
        'title',
        'visibility',
        'where',
        'workflow_state_id',
    )
    ITEM_API_FIELDS = ITEM_API_READ_ONLY_FIELDS + ITEM_API_UPDATABLE_FIELDS

    ITEM_LIST_FIELD = (
        'channel', 'content', 'created_at', 'created_by', 'created_by_external_email',
        'id', 'idea_state', 'item_type', 'language', 'project', 'publication_dt',
        'targets', 'tasks', 'title', 'url', 'workflow_state'
    )

    def assert_common_api_item_fields(self, item):
        self.assertEqual(set(self.ITEM_API_FIELDS), set(item.keys()))

    def assert_api_item_list_fields(self, item):
        self.assertEqual(set(self.ITEM_LIST_FIELD), set(item.keys()))


class ItemApiTest(ItemAPIMixin, PilotAdminUserMixin, WorkflowStateTestingMixin, APITestCase):
    """ Test the API on a single Item ( except content, which is its own beast on a separate module ) """
    longMessage = True

    def test_api_item(self):
        item = items_factories.ItemFactory(desk=self.desk)
        item_pk = item.pk
        api_item_url = reverse(API_ITEMS_DETAIL_URL, kwargs={'pk': item_pk})
        # Correct GET request
        response = self.client.get(api_item_url,
                                   format='json')
        # The response contains the json for the requested item
        item_json = json.loads(response.content)
        self.assert_common_api_item_fields(item_json)

        state = self.get_state_publication_ready()
        my_body = {"type":"doc","content":[{"type":"paragraph","content":[{"type":"text","text":"Awesome body"}]}]}
        content = {
            'title': u'Awesome title',
            'body': my_body
        }
        annotations = {}
        update_data = {
            'workflow_state_id': state.id,
            'content': content,
            'annotations': annotations
        }

        # =====================================
        # Successful update through PUT
        # =====================================

        response = self.client.put(api_item_url,
                                   data=update_data,
                                   format='json')

        # The response contains the json for the updated item
        item_json = json.loads(response.content)
        self.assert_common_api_item_fields(item_json)
        self.assertEqual(item_json['workflow_state_id'], state.id)
        self.assertEqual(item_json['content'], content)
        self.assertEqual(item_json['annotations'], annotations)

        # The db instance is updated
        item = Item.objects.get(pk=item_pk)
        self.assertEqual(item.workflow_state, state)
        self.assertEqual(item.content, content)
        self.assertEqual(item.annotations, annotations)

        # An activity_stream has been created
        activity_stream = Activity.activities_for(item)
        self.assertEqual(1, len(activity_stream))

        self.assert_common_api_item_fields(item_json)

        # =====================================
        # Read-only on PUT
        # =====================================

        # These attributes are read-only, and cannot be updated through a PUT
        for field_name in self.ITEM_API_READ_ONLY_FIELDS:
            if field_name == 'updated_at':
                continue

            old_value = item_json[field_name]
            new_value = 'meh' if (field_name != 'visibility') else 'hidden'

            response = self.client.put(api_item_url,
                                       data={field_name: new_value},
                                       format='json')
            self.assertEqual(response.status_code, 200, msg="field '{}' content : '{}'".format(field_name,json.loads(response.content)))
            item_json = json.loads(response.content)
            new_value = item_json[field_name]
            self.assertEqual(old_value, new_value, msg="field '{}'".format(field_name))

        # =====================================
        # Validation errors on PUT
        # =====================================

        # Annotations should be a dict
        incorrect_update_data = update_data.copy()
        incorrect_update_data['annotations'] = 'meh ?!?'
        response = self.client.put(api_item_url,
                                   data=incorrect_update_data,
                                   format='json')
        self.assertEqual(response.status_code, 400)
        item_json = json.loads(response.content)
        self.assertListEqual(item_json['annotations'], ['Attendait un dictionnaire d\'éléments mais a reçu "unicode".'])

        item_type = item_types_factories.ItemTypeFactory.create(
            desk=self.desk,
            content_schema=SIMPLE_TEST_SCHEMA
        )
        item.item_type = item_type
        item.save()
        incorrect_update_data = update_data.copy()
        incorrect_update_data['content'] = {'integer': 'abc'}
        response = self.client.put(api_item_url,
                                   data=incorrect_update_data,
                                   format='json')
        self.assertEqual(response.status_code, 400)
        item_json = json.loads(response.content)
        self.assertListEqual(item_json['content']['integer'], ['Un nombre entier valide est requis.'])

    def test_api_item_annotations(self):
        """ Test annotation add attached to Item objects."""
        item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk
        )
        # Refresh the cached item instance to ensure to fetch the RelatedFactory results (i.e. the EditSession obj).
        item = Item.objects.get(pk=item.pk)

        url = reverse(API_ITEMS_DETAIL_URL, kwargs={'pk': item.pk})

        # Test PUT of an annotation
        json_sender = {
            "id": 2,
            "username": "john",
            "avatar": "http://domain.com/avatar.png"
        }
        annotation_1 = {
            "id": "123",
            "mainComment": {
                "date": "2016-07-01T14:36:04.702Z",
                "text": "lorème ipsumé",
                "user": json_sender
            },
            "comments": [{
                "date": "2016-07-01T14:37:04.702Z",
                "text": "lorème ipsumé",
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
        annotation_2 = {
            "id": "456",
            "mainComment": {
                "date": "2016-07-01T14:38:04.702Z",
                "text": "dolor sït amêt",
                "user": json_sender
            },
            "comments": [{
                "date": "2016-07-01T14:39:04.702Z",
                "text": "dolor sït amêt",
                "user": json_sender
            }],
            "resolved": False,
            "resolvedBy": None,
            "range": {
                "from": 30,
                "to": 35
            },
            "selectedText": "bleh!"
        }
        json_item = {
            'annotations': {
                'body': {
                    '123': annotation_1,
                    '456': annotation_2
                }
            }
        }

        response = self.client.put(url, data=json_item, format='json')
        self.assertEqual(response.status_code, 200)

        # Refresh
        item = Item.objects.get(pk=item.pk)
        session = item.last_session

        self.assertTrue('avatar' in item.annotations['body']['123']['mainComment']['user'])

        self.assertEqual(item.annotations['body']['123']['mainComment']['user']['avatar'],
                         "http://domain.com/avatar.png")
        self.assertEqual(item.annotations['body']['123'], annotation_1)
        self.assertEqual(item.annotations['body']['456'], annotation_2)
        self.assertEqual(len(item.annotations['body']), 2)
        self.assertEqual(len(session.annotations['body']), 2)

        # We can PUT another annotation dict to update the annotations
        json_item['annotations']['body']['456']['resolved'] = True
        response = self.client.put(url, data=json_item, format='json')
        self.assertEqual(response.status_code, 200)
        item = Item.objects.get(pk=item.pk)
        self.assertEqual(item.annotations['body']['456']['resolved'], True)

        # Incorrect data
        annotation_1['mainComment']['date'] = 'this is obviously not a date'
        response = self.client.put(url, data=json_item, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, {'annotations': {'mainComment': {'date': [
            "La date + heure n'a pas le bon format. Utilisez un des formats suivants : iso-8601."
        ]}}})
        item = Item.objects.get(pk=item.pk)
        session = item.last_session
        self.assertEqual(len(item.annotations['body']), 2)
        self.assertEqual(len(session.annotations['body']), 2)

        del annotation_1['mainComment']
        response = self.client.put(url, data=json_item, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.data, {'annotations': {'mainComment': ['Ce champ est obligatoire.']}})
        item = Item.objects.get(pk=item.pk)
        session = item.last_session
        self.assertEqual(len(item.annotations['body']), 2)
        self.assertEqual(len(session.annotations['body']), 2)

    def test_api_item_annotations_without_avatar(self):
        """ Test annotation add attached to Item objects."""

        item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk
        )

        url = reverse(API_ITEMS_DETAIL_URL, kwargs={'pk': item.pk})
        json_sender = {
            "id": 2,
            "username":"john",
            "avatar": None,
        }
        annotation_1 = {
            "id": "123",
            "mainComment":{
                "date":"2016-07-01T14:36:04.702Z",
                "text":"lorème ipsumé",
                "user":json_sender
            },
            "comments":[],
            "resolved": False,
            "resolvedBy":None,
            "range":{
                "from":20,
                "to":25
            },
            "selectedText": "meh!!"
        }
        json_item = {
            'annotations': {
                'body':{
                    '123': annotation_1,
                }
            }
        }

        response = self.client.put(url, data=json_item, format='json')
        self.assertEqual(response.status_code, 200)

    def test_api_access_to_private_item(self):
        self.desk.private_items_enabled = True
        self.desk.save()

        item = items_factories.ItemFactory(desk=self.desk, is_private=True)
        item_pk = item.pk
        api_item_url = reverse(API_ITEMS_DETAIL_URL, kwargs={'pk': item_pk})

        other_user = pilot_users_factories.EditorFactory.create(password='password')
        self.organization.users.add(other_user)
        self.desk.users.add(other_user)

        # Owner can see the private item
        response = self.client.get(api_item_url, format='json')
        item_json = json.loads(response.content)
        self.assert_common_api_item_fields(item_json)

        # But a random non-admin guy from the same desk cannot
        self.client.login(email=other_user.email, password='password')
        response = self.client.get(api_item_url, format='json')
        self.assertEqual(response.status_code, 403) # Forbidden
        self.assertDictEqual(json.loads(response.content), {"detail": "Cet item est privé"})

        # Owner can update the is_private attribute
        self.client.login(email=self.user.email, password='password')
        update_data = {'is_private': False}
        self.client.put(api_item_url,
                       data=update_data,
                       format='json')
        # The db instance is updated
        item = Item.objects.get(pk=item_pk)
        self.assertFalse(item.is_private)

        # But the random non-admin guy cannot, even if its public
        self.client.login(email=other_user.email, password='password')
        update_data = {'is_private': True}
        self.client.put(api_item_url,
                       data=update_data,
                       format='json')
        # The db instance is NOT updated
        item = Item.objects.get(pk=item_pk)
        self.assertFalse(item.is_private)


class ItemListApiTest(ItemAPIMixin, PilotAdminUserMixin,
                      WorkflowStateTestingMixin, ItemTypeTestingMixin, APITestCase):
    """ Test the API for lists of Items """

    def setUp(self):
        super(ItemListApiTest, self).setUp()

        # Create 2 channels related to the current desk.
        self.channel1 = channels_factories.ChannelFactory.create(desk=self.desk)
        self.channel_parent = channels_factories.ChannelFactory.create(desk=self.desk)
        self.channel2 = channels_factories.ChannelFactory.create(desk=self.desk, parent=self.channel_parent)
        self.channel3 = channels_factories.ChannelFactory.create(desk=self.desk)

        # Create 2 targets related to the current desk.
        self.target1 = targets_factories.TargetFactory.create(desk=self.desk)
        self.target2 = targets_factories.TargetFactory.create(desk=self.desk)
        self.target3 = targets_factories.TargetFactory.create(desk=self.desk)
        self.target4 = targets_factories.TargetFactory.create(desk=self.desk)

        # Create a custom item type.
        self.item_type = item_types_factories.ItemTypeFactory.create(desk=self.desk)

        # Create a bunch of confirmed items (outside of `IdeaStorm`).
        self.items1 = items_factories.ConfirmedItemFactory.create_batch(
            size=5,
            desk=self.desk,
            channel=self.channel1,
            targets=[self.target1]
        )
        self.items2 = items_factories.ConfirmedItemFactory.create_batch(
            size=5,
            desk=self.desk,
            channel=self.channel2,
            targets=[self.target2]
        )
        self.items3 = items_factories.ConfirmedItemTweetFactory.create_batch(
            size=5,
            desk=self.desk,
            channel=self.channel_parent,
            targets=[self.target3]
        )
        self.items4 = items_factories.ConfirmedItemTweetFactory.create_batch(
            size=2,
            desk=self.desk,
            channel=self.channel3,
            targets=[self.target4],
            item_type=self.item_type
        )
        self.items_all = Item.objects.filter(desk=self.desk)

        self.items_in_trash = items_factories.ItemFactory.create_batch(
            size=2,
            desk=self.desk,
            channel=self.channel3,
            in_trash=True
        )
        self.items_hidden = items_factories.ItemFactory.create_batch(
            size=3,
            desk=self.desk,
            channel=self.channel3,
            in_trash=False
        )

    def test_api_items_list(self):
        """Test the API_ITEMS_LIST_URL method """

        response = self.client.get(reverse(API_ITEMS_LIST_URL), format='json')
        content = json.loads(response.content)

        self.assertEqual(17, content['count'])
        self.assertEqual(2, content['num_pages'])
        self.assertEqual(len(self.items_all), len(content['objects']) + 2)

        self.assert_api_item_list_fields(content['objects'][0])
        # language == null if desk international mode is disabled
        self.assertFalse(self.desk.item_languages_enabled)
        self.assertIsNone(content['objects'][0]['language'])

        # Enabling international mode
        desk = Desk.objects.get(pk=self.desk.pk)
        desk.item_languages_enabled = True
        desk.allowed_languages = ['fr_FR', 'en_us']
        desk.save()
        response = self.client.get(reverse(API_ITEMS_LIST_URL), format='json')
        content = json.loads(response.content)
        self.assertTrue('language' in content['objects'][0])

    def test_api_trash_list(self):
        """Test the 'api_trash_list' method for items in trash."""

        response = self.client.get(reverse('api-items-trash-list'), format='json')

        content = json.loads(response.content)

        self.assertEqual(2, content['count'])
        self.assertEqual(1, content['num_pages'])
        self.assertEqual(len(self.items_in_trash), len(content['objects']))

        self.assert_api_item_list_fields(content['objects'][0])
        # language == null if desk international mode is disabled
        self.assertFalse(self.desk.item_languages_enabled)
        self.assertIsNone(content['objects'][0]['language'])

        # Enabling international mode
        desk = Desk.objects.get(pk=self.desk.pk)
        desk.item_languages_enabled = True
        desk.allowed_languages = ['fr_FR', 'en_us']
        desk.save()
        response = self.client.get(reverse(API_ITEMS_LIST_URL), format='json')
        content = json.loads(response.content)
        self.assertTrue('language' in content['objects'][0])

    def test_api_items_list_filter(self):
        """ Test filtering """

        # Filter by channel1 and target1.
        url_query_string = '{0}?channels={1}&targets={2}'.format(
            reverse(API_ITEMS_LIST_URL), self.channel1.pk, self.target1.pk)
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(self.items1), content['count'])
        self.assertEqual(1, content['num_pages'])
        self.assertEqual(len(self.items1), len(content['objects']))

        # Filter by channel1 and channel2. This should be cumulative.
        url_query_string = '{0}?channels={1}&channels={2}'.format(
            reverse(API_ITEMS_LIST_URL), self.channel1.pk, self.channel2.pk)
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(self.items1) + len(self.items2), content['count'])
        self.assertEqual(1, content['num_pages'])
        self.assertEqual(len(self.items1) + len(self.items2), len(content['objects']))

        # Filter by target2.
        url_query_string = '{0}?targets={1}'.format(reverse(API_ITEMS_LIST_URL), self.target2.pk)
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(self.items2), content['count'])
        self.assertEqual(1, content['num_pages'])
        self.assertEqual(len(self.items2), len(content['objects']))

        # Filter by multiple states. This should be cumulative.
        state1 = self.get_state_publication_ready()
        state2 = self.get_state_validation_ready()
        state1_num = Item.objects.filter(desk=self.desk, workflow_state=state1).count()
        state2_num = Item.objects.filter(desk=self.desk, workflow_state=state2).count()
        url_query_string = '{0}?workflow_state={1}&workflow_state={2}'.format(reverse(API_ITEMS_LIST_URL), state1.id, state2.id)
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(state1_num + state2_num, content['count'])

        # Filter by twitter type
        twitter_type = self.get_item_type_twitter()
        twitter_num = Item.objects.filter(desk=self.desk, item_type=twitter_type).count()
        url_query_string = '{0}?item_type={1}'.format(reverse(API_ITEMS_LIST_URL), twitter_type.id)
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(twitter_num, content['count'])

        # Filter by user defined item type
        item_type_num = Item.objects.filter(desk=self.desk,
                                                                item_type=self.item_type).count()
        url_query_string = '{0}?item_type={1}'.format(reverse(API_ITEMS_LIST_URL), self.item_type.pk)
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(item_type_num, content['count'])

    def test_api_items_list_filter_by_language(self):
        """ Test filtering """

        items_fr = items_factories.ConfirmedItemFactory.create_batch(
            size=13,
            desk=self.desk,
            channel=self.channel2,
            targets=[self.target2],
            language='fr_FR'
        )

        items_en = items_factories.ConfirmedItemFactory.create_batch(
            size=7,
            desk=self.desk,
            channel=self.channel2,
            targets=[self.target2],
            language='en_US'
        )

        total_count = sum(map(len, [items_fr, items_en, self.items1, self.items2, self.items3, self.items4]))
        without_language_count = sum(map(len, [self.items1, self.items2, self.items3, self.items4]))
        # Enabling international mode
        desk = Desk.objects.get(pk=self.desk.pk)
        desk.item_languages_enabled = True
        desk.allowed_languages = ['fr_FR', 'en_us', 'tr_TR']
        desk.save()

        # No querystring
        url_query_string = reverse(API_ITEMS_LIST_URL)
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(total_count, content['count'])

        # Filtering fench items
        url_query_string = '{0}?language={1}'.format(reverse(API_ITEMS_LIST_URL), 'fr_FR')
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(items_fr), content['count'])

        # Filtering english items
        url_query_string = '{0}?language={1}'.format(reverse(API_ITEMS_LIST_URL), 'en_US')
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(items_en), content['count'])

        # Filtering english + french items. It should be cumulative
        url_query_string = '{0}?language={1}&language={2}'.format(reverse(API_ITEMS_LIST_URL), 'en_US', 'fr_FR')
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(items_en) + len(items_fr), content['count'])

        # Filtering turkish items (there are no turkish items)
        url_query_string = '{0}?language={1}'.format(reverse(API_ITEMS_LIST_URL), 'blank')
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(without_language_count, content['count'])

        # Filtering blank items
        url_query_string = '{0}?language={1}'.format(reverse(API_ITEMS_LIST_URL), 'tr_TR')
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(0, content['count'])

    def test_api_items_list_filter_by_channel_hierarchy(self):
        """Ensure items are retrieved according to hierarchy"""
        url_query_string = '{0}?channels={1}'.format(
            reverse(API_ITEMS_LIST_URL), self.channel_parent.pk)
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        parent_childs = len(self.items2) + len(self.items3)
        self.assertEqual(parent_childs, content['count'])

    def test_api_items_list_filter_by_on(self):
        """Test filtering by exact date."""

        on_date = Task.objects.aggregate(Min('deadline')).values()[0]
        items_num = Item.objects.filter(tasks__deadline__date=on_date.date()).count()

        url_query_string = '{0}?on={1}'.format(reverse(API_ITEMS_LIST_URL), on_date.strftime('%Y-%m-%d'))
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)

        self.assertEqual(items_num, content['count'])
        self.assertEqual(1, content['num_pages'])
        self.assertEqual(items_num, len(content['objects']))

    def test_api_items_list_filter_by_start(self):
        """Test filtering by start date."""

        start = Task.objects.aggregate(Max('deadline')).values()[0]
        items_num = Item.objects.filter(tasks__deadline__date__gte=start.date()).count()

        url_query_string = '{0}?start={1}'.format(reverse(API_ITEMS_LIST_URL), start.strftime('%Y-%m-%d'))
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)

        self.assertEqual(items_num, content['count'])
        self.assertEqual(1, content['num_pages'])
        self.assertEqual(items_num, len(content['objects']))
    def test_api_items_list_filter_by_start_and_end(self):
        """Test filtering by start and end dates."""

        start = Task.objects.filter(item__channel=self.channel1).aggregate(Min('deadline')).values()[0]
        end = Task.objects.filter(item__channel=self.channel1).aggregate(Max('deadline')).values()[0]

        url_query_string = '{0}?start={1}&end={2}'.format(
            reverse(API_ITEMS_LIST_URL),
            start.strftime('%Y-%m-%d'),
            end.strftime('%Y-%m-%d')
        )
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(self.items1), content['count'])
        self.assertEqual(1, content['num_pages'])
        self.assertEqual(len(self.items1), len(content['objects']))

    def test_api_items_list_filter_by_period(self):
        """Test filtering by period."""

        start = make_naive(timezone.now())
        end = start + datetime.timedelta(hours=SavedFilter.PERIOD_WEEK_IN_HOURS)

        items_for_next_week_num = Item.objects.filter(tasks__deadline__range=(start, end)).count()

        url_query_string = '{0}?period={1}'.format(
            reverse(API_ITEMS_LIST_URL),
            SavedFilter.PERIOD_WEEK_IN_HOURS
        )
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(items_for_next_week_num, content['count'])
        self.assertEqual(1, content['num_pages'])
        self.assertEqual(items_for_next_week_num, len(content['objects']))

    def test_setup_desk_assignations(self):

        for item in self.items_all:
            self.assertEqual(item.desk, item.channel.desk)

            for target in item.targets.all():
                self.assertEqual(item.desk, target.desk)


class BackgridItemsFilterApiTest(ItemAPIMixin, PilotAdminUserMixin, APITestCase):
    """Test the API for items fetched via Backgrid."""

    def checkout_response(self, url_query_string, expected_nb):
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(expected_nb, len(content['objects']))

    def test_filter_owners(self):
        user1 = pilot_users_factories.AdminFactory.create(password='password', username='user1')
        user2 = pilot_users_factories.AdminFactory.create(password='password', username='user2')
        items_factories.ConfirmedItemFactory.create(desk=self.desk, owners=[])
        items_factories.ConfirmedItemFactory.create(desk=self.desk, owners=[user1.pk])
        items_factories.ConfirmedItemFactory.create(desk=self.desk, owners=[user1.pk, user2.pk])

        self.checkout_response(reverse(API_ITEMS_LIST_URL), 3)
        self.checkout_response('{0}?owners={1}'.format(reverse(API_ITEMS_LIST_URL), user2.pk), 1)
        self.checkout_response('{0}?owners={1}&owners={2}'.format(reverse(API_ITEMS_LIST_URL), user2.pk, user1.pk), 2)


class CalendarItemsApiTest(ItemAPIMixin, PilotAdminUserMixin, WorkflowStateTestingMixin, APITestCase):
    """Test the API for items fetched via FullCalendar."""

    def test_api_calendar_items_list(self):
        """Test the 'api_calendar_items_list' method used via FullCalendar."""

        url = reverse('api-items-calendar')

        # Create a bunch of confirmed items
        # ItemFactory will create an Item per day, see `publication_dt` factory.Sequence().
        items = items_factories.ConfirmedItemFactory.create_batch(size=10, desk=self.desk)

        # Get the min and max `publication_dt` as start and end.
        start = Task.objects.aggregate(Min('deadline')).values()[0]
        end = Task.objects.aggregate(Max('deadline')).values()[0]

        # Call 'api_calendar_items_list' for Item between start and end.
        url_query_string = '{0}?start={1}&end={2}'.format(url, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))

        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(content), len(items))
        self.assert_api_item_list_fields(content[0])

        # Ensure that the response contains private URLs.
        urls = [i['url'] for i in content]
        for item in items:
            self.assertIn(item.get_absolute_url(), urls)

        # Change start and end values. Search for nonexistent Item.
        start = start - datetime.timedelta(days=31)
        end = start + datetime.timedelta(days=20)
        url_query_string = '{0}?start={1}&end={2}'.format(url, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        response = self.client.get(url_query_string, format='json')
        self.assertEqual(len(json.loads(response.content)), 0)

    def test_api_calendar_items_list_filtering(self):
        """Test the 'api_calendar_items_list' method used via FullCalendar."""

        url = reverse('api-items-calendar')

        published_items = items_factories.ItemFactory.create_batch(
            size=7, desk=self.desk, workflow_state=self.get_state_published())
        validation_ready_items = items_factories.ItemFactory.create_batch(
            size=5, desk=self.desk, workflow_state=self.get_state_validation_ready())

        # Project and associated items
        project = projects_factories.ProjectFactory(desk=self.desk, state='closed')
        project_items = items_factories.ItemFactory.create_batch(
            size=3, desk=self.desk, workflow_state=self.get_state_published(), project=project)

        # Get the min and max `publication_dt` as start and end.
        start = Task.objects.aggregate(Min('deadline')).values()[0]
        end = Task.objects.aggregate(Max('deadline')).values()[0]

        # Call 'api_calendar_items_list' for Item between start and end.
        url_query_string = '{0}?start={1}&end={2}&workflow_state={3}'.format(
            url,
            start.strftime('%Y-%m-%d'),
            end.strftime('%Y-%m-%d'),
            self.get_state_published().id
        )

        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(content), len(published_items) + len(project_items))

        # Filtering on item state.
        url_query_string = '{0}?start={1}&end={2}&workflow_state={3}'.format(
            url, start.strftime('%Y-%m-%d'),
            end.strftime('%Y-%m-%d'),
            self.get_state_validation_ready().id
        )

        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(content), len(validation_ready_items))

        # Filtering on project state
        url_query_string = '{0}?start={1}&end={2}&project_state=closed'.format(
            url,
            start.strftime('%Y-%m-%d'),
            end.strftime('%Y-%m-%d'))
        response = self.client.get(url_query_string, format='json')
        content = json.loads(response.content)
        self.assertEqual(len(content), len(project_items))

    def test_api_calendar_items_list_perms(self):
        """Test the 'api_calendar_items_list' perms."""

        url = reverse('api-items-calendar')

        # Create another desk for another user.
        other_desk = desks_factories.DeskFactory.create()

        # Create a bunch of items related to the other desk.
        other_items = items_factories.ConfirmedItemFactory.create_batch(size=10, desk=other_desk)

        # Get the min and max `publication_dt` as start and end.
        start = Task.objects.aggregate(Min('deadline')).values()[0]
        end = Task.objects.aggregate(Max('deadline')).values()[0]

        # The current logged user should have no items returned by the API.
        url_query_string = '{0}?start={1}&end={2}'.format(url, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        response = self.client.get(url_query_string, format='json')
        self.assertEqual(len(json.loads(response.content)), 0)
        self.assertEqual(0, self.user.desks.all()[0].items.all().count())

        self.client.logout()

        # Log the other user in.
        self.client.login(email=other_desk.created_by.email, password='password')

        # All items of the other user should be returned by the API.
        url_query_string = '{0}?start={1}&end={2}'.format(url, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        response = self.client.get(url_query_string, format='json')
        self.assertEqual(len(json.loads(response.content)), len(other_items))

        self.client.logout()

    def test_api_calendar_shared_items_list(self):
        """Test the public 'api_calendar_shared_items_list' method used via FullCalendar."""

        # Create 2 projects related to the current desk.
        project1 = projects_factories.ProjectFactory.create(desk=self.desk)
        project2 = projects_factories.ProjectFactory.create(desk=self.desk)

        # Create 5 confirmed items related to project1.
        items_factories.ConfirmedItemFactory.create_batch(size=5, desk=self.desk, project=project1)
        # Create 5 confirmed items related to project2.
        items_factories.ConfirmedItemFactory.create_batch(size=5, desk=self.desk, project=project2)

        # Get the min and max `publication_dt` as start and end.
        start = Task.objects.aggregate(Min('deadline')).values()[0]
        end = Task.objects.aggregate(Max('deadline')).values()[0]

        # Create a saved filter for the current logged user.
        saved_filter = items_factories.SavedFilterFactory.create(
            user=self.user,
            desk=self.desk,
            type=SavedFilter.TYPE_CALENDAR,
            filter='start={0}&end={1}&project={2}'.format(
                start.strftime('%Y-%m-%d'),
                end.strftime('%Y-%m-%d'),
                project1.pk
            )
        )

        # Create a shared filter.
        shared_filter = items_factories.PublicSharedFilterFactory.create(saved_filter=saved_filter)

        # Logout the current user.
        self.client.logout()

        url = reverse(
            'api-items-shared-calendar/(?P<shared-filter-pk>\d+)/(?P<token>\w+)',
            kwargs={'shared_filter_pk': shared_filter.pk, 'token': shared_filter.token, }
        )
        url_query_string = '{0}?{1}'.format(url, saved_filter.query)
        response = self.client.get(url_query_string, format='json')
        json_response = json.loads(response.content)

        # Ensure a public call to the 'api_calendar_shared_items_list' method is possible.
        # Ensure that only items related to project1 are displayed.
        self.assertEqual(len(json_response), Item.objects.filter(project=project1).count())

        # Ensure that the response contains public URLs.
        urls = [i['url'] for i in json_response]
        for item in Item.objects.filter(project=project1):
            public_url = reverse('ui_shared_item_details', kwargs={
                'item_pk': item.pk,
                'shared_filter_pk': shared_filter.pk,
                'token': shared_filter.token,
            })
            self.assertIn(public_url, urls)

        # language == null if desk international mode is disabled
        self.assertFalse(self.desk.item_languages_enabled)
        self.assertIsNone(json_response[0]['language'])

        # Enabling international mode
        desk = Desk.objects.get(pk=self.desk.pk)
        desk.item_languages_enabled = True
        desk.allowed_languages = ['fr_FR', 'en_us']
        desk.save()
        response = self.client.get(url_query_string, format='json')
        json_response = json.loads(response.content)
        self.assertTrue('language' in json_response[0])


class ItemsApiForRestrictedEditorsTest(PilotRestrictedEditorUserMixin, APITestCase):
    """Test the API for items fetched by a restricted editor."""

    def setUp(self):
        super(ItemsApiForRestrictedEditorsTest, self).setUp()

        # Create 2 channels related to the current desk.
        self.channel1 = channels_factories.ChannelFactory.create(desk=self.desk)
        self.channel2 = channels_factories.ChannelFactory.create(desk=self.desk)
        self.channel3 = channels_factories.ChannelFactory.create(desk=self.desk)

        self.project = projects_factories.ProjectFactory(desk=self.desk)
        # Create a custom item type.
        self.item_type = item_types_factories.ItemTypeFactory.create(desk=self.desk)

        # Create a bunch of confirmed items (outside of `IdeaStorm`).
        self.items1 = items_factories.ConfirmedItemFactory.create_batch(
            size=5,
            desk=self.desk,
            channel=self.channel1,
        )

        self.items2 = items_factories.ConfirmedItemFactory.create_batch(
            size=3,
            desk=self.desk,
            channel=self.channel2,
            project=self.project,
        )
        self.items3 = items_factories.ConfirmedItemTweetFactory.create_batch(
            size=5,
            desk=self.desk,
        )
        self.items4 = items_factories.ConfirmedItemTweetFactory.create_batch(
            size=2,
            desk=self.desk,
            channel=self.channel3,
            item_type=self.item_type
        )
        self.items_all = Item.objects.filter(desk=self.desk)

    def test_api_items_list(self):
        """ Test the API_ITEMS_LIST_URL method, for restricted editors """

        response = self.client.get(reverse(API_ITEMS_LIST_URL), format='json')

        content = json.loads(response.content)

        # Restricted editors can't see any item
        self.assertEqual(0, content['count'])

        # Restricted editor can see items because he owns an item channel
        self.channel1.owners.add(self.restricted_user)
        response = self.client.get(reverse(API_ITEMS_LIST_URL), format='json')

        content = json.loads(response.content)

        self.assertEqual(5, content['count'])
        self.channel1.owners.clear()

        # Restricted editor can see items because he owns an item
        self.items2[0].owners.add(self.restricted_user)
        response = self.client.get(reverse(API_ITEMS_LIST_URL), format='json')

        content = json.loads(response.content)

        self.assertEqual(1, content['count'])
        self.items2[0].owners.clear()

        # Restricted editor can see items because he created an item
        self.items1[0].created_by = self.restricted_user
        self.items1[0].save()
        response = self.client.get(reverse(API_ITEMS_LIST_URL), format='json')

        content = json.loads(response.content)

        self.assertEqual(1, content['count'])
        self.items1[0].delete()

        # Restricted editor can see items because he owns an item project
        self.project.owners.add(self.restricted_user)
        response = self.client.get(reverse(API_ITEMS_LIST_URL), format='json')

        content = json.loads(response.content)

        self.assertEqual(3, content['count'])
