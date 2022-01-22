import datetime
import json
import random
import copy
from unittest.case import skip

import pytz
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from django.utils.encoding import force_str
from django.contrib.contenttypes.models import ContentType

import pilot.items.forms as items_forms
from pilot.assets.tests import factories as assets_factories
from pilot.activity_stream.models import Activity
from pilot.items.tests.test_api import API_ITEMS_DETAIL_URL
from pilot.projects.tests import factories as projects_factories
from pilot.channels.tests import factories as channels_factories
from pilot.desks.tests import factories as desks_factories
from pilot.desks.models import Desk
from pilot.items.tests import factories as items_factories
from pilot.item_types import initial_item_types
from pilot.pilot_users.tests import factories as user_factories
from pilot.pilot_users.models import PERMISSION_EDITORS
from pilot.social.factories import FacebookLogFactory, TweetLogFactory
from pilot.targets.tests import factories as targets_factories
from pilot.utils import states
from pilot.utils.test import PilotAdminUserMixin, prosemirror_body, prosemirror_body_string, \
    WorkflowStateTestingMixin
from pilot.utils.prosemirror.prosemirror import prosemirror_json_to_text
from pilot.item_types.tests.testing_item_type_definition import VALIDATION_TEST_SCHEMA
from pilot.item_types.tests import factories as item_types_factories


class MainCalendarUiTest(PilotAdminUserMixin, TestCase):
    def setUp(self):
        super(MainCalendarUiTest, self).setUp()
        self.owners = user_factories.PilotUserFactory.create_batch(2)
        self.desk.users.add(*self.owners)

    def test_main_calendar(self):
        """Test the main calendar view."""
        url = reverse('ui_main_calendar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @skip("BigFilter has been Vueified, this test should be rewritten")
    def test_big_filter_in_items_list(self):
        """Test the main list view."""

        items_factories.ConfirmedItemFactory.create_batch(size=10, desk=self.desk, owners=self.owners)
        channels = channels_factories.ChannelFactory.create_batch(size=10, desk=self.desk)
        projects = projects_factories.ProjectFactory.create_batch(size=10, desk=self.desk)
        targets = targets_factories.TargetFactory.create_batch(size=10, desk=self.desk)
        url = reverse('ui_main_calendar')
        # Test bigfilter dropdown with desk international mode disabled
        response = self.client.get(url)
        self.assertContains(response, 'big-filter')
        self.assertNotContains(response, '<optgroup label="Langues">')
        self.assertContains(response, '<optgroup label="Cibles">')
        for target in targets:
            self.assertContains(response, '<option value="targets={0}">{1}</option>'.format(target.pk, target.name))
        self.assertContains(response, '<optgroup label="Projets">')
        for project in projects:
            self.assertContains(response,
                                '<option value="project={0}">{1}</option>'.format(project.pk, project.name))
        self.assertContains(response, '<optgroup label="États des contenus">')
        self.assertContains(response, '<optgroup label="États des projets">')  # Only displayed on Calendars
        for state in self.desk.workflow_states.all():
            self.assertContains(response, '<option value="workflow_state={0}">{1}</option>'.format(state.id, state.label))
        self.assertContains(response, '<optgroup label="Canaux">')
        for channel in channels:
            self.assertContains(response, '<option value="channel={0}">{1}</option>'.format(channel.pk, channel.hierarchy))

        # Test bigfilter dropdown with desk international mode enabled
        # Desk.objects.all()[1].delete()
        d = Desk.objects.get(pk=self.desk.pk)
        d.item_languages_enabled = True
        d.allowed_languages = ['fr_FR', 'en_US', 'tr_TR']
        d.save()
        response = self.client.get(url)

        # This triggers the `language` column display - must be visible there
        self.assertContains(response, '<optgroup label="Langues">')
        self.assertContains(response, '<option value="language=fr_FR">Français</option>')


class ItemFormTest(PilotAdminUserMixin, WorkflowStateTestingMixin, TestCase):

    def setUp(self):
        super(ItemFormTest, self).setUp()
        self.owners = user_factories.PilotUserFactory.create_batch(2)
        self.desk.users.add(*self.owners)
        self.publication_dt = (timezone.now() + datetime.timedelta(days=10))
        self.user_timezone =  pytz.timezone('Europe/Paris')
        self.body_json = prosemirror_body(u'Item content ünicôdé')
        self.body_unicode = prosemirror_body_string(u'Item content ünicôdé')
        self.scope_choices = (list(zip(*Item.SCOPE_CHOICES)) + [None])[0]

    def check_get(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response

    def check_post(self, url, post_data):
        response = self.client.post(url, data=post_data)
        item = Item.objects.latest('created_at')
        item_url = reverse('ui_item_details', kwargs={'item_pk': item.pk})
        self.assertRedirects(response, item_url)
        return item

    def check_display_input(self, response, expected_fields=['title', 'publication_dt', 'owners']):
        content = response.content.decode('utf-8')
        for field in expected_fields:
            id_attr = 'id="id_{0}"'.format(field)
            name_attr = 'name="{0}"'.format(field)
            self.assertIn(id_attr, content, "%s not found in html" % field)
            self.assertIn(name_attr, content, "%s not found in html" % field)

    def check_not_display_input(self, response, not_expected_fields=['body', 'project', 'channel', 'targets',
                                                                     'publication_date', 'publication_time', 'addanother']):
        content = response.content.decode('utf-8')
        for field in not_expected_fields:
            id_attr = 'id="id_{0}"'.format(field)
            name_attr = 'name="{0}"'.format(field)
            self.assertNotIn(id_attr, content, "%s found in html" % field)
            self.assertNotIn(name_attr, content, "%s found in html" % field)

    def check_item(self, item, post_data, with_targets=False, with_owners=False, check_body=True):
        self.assertEqual(item.desk, self.desk)
        self.assertEqual(item.publication_dt.astimezone(self.user_timezone).date(), self.publication_dt.date())
        self.assertEqual(item.title, post_data['title'])
        if check_body:
            self.assertEqual(item.content['body'], self.body_json)
        if with_targets:
            # Checking targets. We use set to order lists.
            self.assertEqual(
                set([target.pk for target in item.targets.all()]),
                set(post_data['targets'])
            )
        if with_owners:
            # Checking owners. We use set to order lists.
            self.assertEqual(
                set([o.pk for o in item.owners.all()]),
                set(post_data['owners'])
            )

    def check_guidelines(self, item, post_data):
        self.assertEqual(item.guidelines, post_data['guidelines'])
        self.assertEqual(item.where, post_data['where'])
        self.assertEqual(item.goal, post_data['goal'])
        self.assertEqual(item.contacts, post_data['contacts'])
        self.assertEqual(item.sources, post_data['sources'])
        self.assertEqual(item.available_pictures, post_data['available_pictures'])
        self.assertEqual(item.photographer_needed, post_data['photographer_needed'])
        self.assertEqual(item.investigations_needed, post_data['investigations_needed'])
        self.assertEqual(item.support_needed, post_data['support_needed'])
        self.assertEqual(item.photo_investigations_needed, post_data['photo_investigations_needed'])

@skip("Test obsoleted by the new Vue.js UI")
class ItemsAddUiTest(ItemFormTest):
    """Test C on Item objects."""
    ALLOWED_LANGUAGES = ['fr_FR', 'es_ES', 'fi_FI']

    def setUp(self):
        super(ItemsAddUiTest, self).setUp()
        # Keep a reference to the list view URL.
        self.main_items_list_url = reverse('ui_items_list')

    def post_data(self, has_targets=True, has_owners=False, is_tweet=False, is_facebook=False):
        post_data=  {
            'available_pictures': bool(random.getrandbits(1)),
            'body': self.body_unicode,
            'contacts': u'Item contacts ünicôdé',
            'goal': u'Item goal ünicôdé',
            'guidelines': u'Item guidelines ünicôdé',
            'investigations_needed': bool(random.getrandbits(1)),
            'photo_investigations_needed': bool(random.getrandbits(1)),
            'photographer_needed': bool(random.getrandbits(1)),
            'scope': random.choice(self.scope_choices),
            'sources': u'Item source ünicôdé',
            'support_needed': bool(random.getrandbits(1)),
            'title': u'Item title ünicôdé',
            'where': u'Item where ünicôdé',
        }
        if is_tweet or is_facebook:
            post_data.update({'publication_date': self.publication_dt.strftime('%Y-%m-%d'),
                              'publication_time': self.publication_dt.strftime('%H:%M')})
        else:
            post_data['publication_dt'] = self.publication_dt.strftime('%Y-%m-%d')
        if has_targets:
            target1 = targets_factories.TargetFactory(desk=self.desk)
            target2 = targets_factories.TargetFactory(desk=self.desk)
            post_data['targets'] = [target1.pk, target2.pk]
        if has_owners:
            post_data['owners'] = [o.pk for o in self.owners]

        return post_data



    def check_queryset(self, response, field, expected_set):
        queryset = response.context['form'][field].field.queryset
        self.assertEqual(queryset.count(), expected_set.count())
        # Only owners belonging to current desk should be shown.
        for owner in queryset:
            self.assertTrue(owner in expected_set)

    def check_post_with_no_redirect(self, url, post_data):
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 200)
        return response

    def check_full_datetime(self, item):
        self.assertEqual(
            item.publication_dt.astimezone(self.user_timezone).strftime('%d %m %Y %H:%M'),
            self.publication_dt.strftime('%d %m %Y %H:%M')
        )

    def check_snapshot_added(self, item, post_data):
        session = EditSession.objects.get(item=item)
        self.assertEqual(session.title, post_data['title'])
        self.assertEqual(session.content['body'], self.body_json)
        self.assertEqual(session.version, '1.0')
        self.assertEqual(session.created_by, item.created_by)

    def test_get_with_no_projects_channel_and_targets_in_db(self):
        """Test get default form for add item when there is no projects, channels or targets"""

        response = self.check_get(reverse('ui_item_add'))
        self.check_display_input(response)
        self.check_not_display_input(response)

    def test_get_with_projects_channels_and_targets_in_db(self):
        """Test get default form for add item"""
        projects_factories.ProjectFactory.create(desk=self.desk)
        targets_factories.TargetFactory(desk=self.desk)
        channels_factories.ChannelFactory(desk=self.desk)
        response = self.check_get(reverse('ui_item_add'))
        self.check_display_input(response, ['title', 'publication_dt', 'owners', 'project', 'channel', 'targets'])
        self.check_not_display_input(response, ['publication_date', 'publication_time'])
        queryset = response.context['form']['project'].field.queryset
        self.check_queryset(response, 'project', self.desk.projects.all())
        self.check_queryset(response, 'targets', self.desk.targets.all())
        self.check_queryset(response, 'channel', self.desk.channels.all())

    def test_get_with_owner(self):
        """Test owner is well set in form add item"""
        response = self.check_get(reverse('ui_item_add'))
        self.check_queryset(response, 'owners', self.desk.users.all())
        self.check_display_input(response)
        self.check_not_display_input(response)

    def test_get_with_project(self):
        """Test get form item add with project"""
        project = projects_factories.ProjectFactory.create(desk=self.desk)
        response = self.check_get(reverse('ui_item_add_with_item_type_and_project',
                                          kwargs={'project_pk': project.pk,'item_type': 'default'}))
        self.check_display_input(response)
        self.check_not_display_input(response)

    def test_get_with_custom_type(self):
        """Test get item add form for a custom type"""
        item_type = item_types_factories.ItemTypeFactory.create(desk=self.desk)
        response = self.check_get(reverse('ui_item_add_with_item_type', args=[item_type.technical_name]))
        self.check_display_input(response)
        self.check_not_display_input(response)

    def test_get_with_custom_type_and_project(self):
        """Test get item add form for a custom type and a given project"""
        project = projects_factories.ProjectFactory.create(desk=self.desk)
        item_type = item_types_factories.ItemTypeFactory.create(desk=self.desk)
        response = self.check_get(reverse('ui_item_add_with_item_type_and_project',
                                          kwargs={'item_type': item_type.technical_name,
                                                  'project_pk': project.pk})
                                  )
        self.check_display_input(response)
        self.check_not_display_input(response)

    def test_get_tweet(self):
        """Test get form add item for a tweet type"""
        response = self.check_get(reverse('ui_item_add_with_item_type', kwargs={'item_type': 'twitter'}))
        self.check_display_input(response, ['title', 'body', 'publication_date', 'publication_time', 'owners', 'addanother'])
        self.check_not_display_input(response,['project', 'channels', 'targets', 'publication_dt'])

    def test_get_tweet_with_project(self):
        project = projects_factories.ProjectFactory.create(desk=self.desk)
        response = self.check_get(reverse('ui_item_add_with_item_type_and_project',
                                          kwargs={'project_pk': project.pk, 'item_type': 'twitter'})
                                 )
        self.check_display_input(response, ['title', 'body', 'publication_date', 'publication_time', 'owners', 'addanother'])
        self.check_not_display_input(response,['project', 'channels', 'targets', 'publication_dt'])

    def test_get_facebook(self):
        """Test get form add item for a facebook type"""
        response = self.check_get(reverse('ui_item_add_with_item_type', kwargs={'item_type': 'facebook'}))
        self.check_display_input(response, ['title', 'publication_date', 'publication_time', 'owners'])
        self.check_not_display_input(response,['body', 'project', 'channels', 'targets', 'publication_dt', 'addanother'])

    def test_get_facebook_with_project(self):
        """Test get form add item for a facebook type and a given project"""
        project = projects_factories.ProjectFactory.create(desk=self.desk)
        response = self.check_get(reverse('ui_item_add_with_item_type_and_project',
                               kwargs={'project_pk': project.pk, 'item_type': 'facebook'})
                       )
        self.check_display_input(response, ['title', 'publication_date', 'publication_time', 'owners'])
        self.check_not_display_input(response,['body', 'project', 'channels', 'targets', 'publication_dt', 'addanother'])

    def test_item_add(self):
        """Test item add."""

        url = reverse('ui_item_add')
        post_data = self.post_data()
        item = self.check_post(url, post_data)

        self.check_item(item, post_data, with_targets=True)
        self.assertEqual(item.item_type, initial_item_types.ARTICLE_TYPE)
        self.check_guidelines(item, post_data)
        self.check_snapshot_added(item, post_data)

    def test_item_add_with_all_metadata(self):
        """Test item add with owner set."""
        projects = projects_factories.ProjectFactory.create_batch(size=10, desk=self.desk)
        channels = channels_factories.ChannelFactory.create_batch(size=10, desk=self.desk)

        url = reverse('ui_item_add')
        post_data = self.post_data(has_targets=True,has_owners=True)
        post_data.update({'project': projects[4].pk,'channel': channels[5].pk})
        item = self.check_post(url, post_data)

        self.check_item(item, post_data, with_targets=True, with_owners=True)
        self.assertEqual(projects[4].pk, item.project.pk)
        self.assertEqual(channels[5].pk, item.channel.pk)
        self.check_snapshot_added(item, post_data)


    def test_item_add_with_project(self):
        """Test item add with project.(from the project detail page)"""

        project = projects_factories.ProjectFactory.create(desk=self.desk)

        url = reverse('ui_item_add_with_item_type_and_project', kwargs={'project_pk': project.pk,
                                                                         'item_type': 'default'})
        post_data = self.post_data(has_targets=False, has_owners=False)
        item = self.check_post(url, post_data)

        self.check_item(item, post_data)
        self.assertEqual(item.project, project)
        self.check_guidelines(item, post_data)

    def test_item_with_custom_type_add(self):
        """Test item addition with custom content type ."""

        item_type = item_types_factories.ItemTypeFactory.create(desk=self.desk)
        url = reverse('ui_item_add_with_item_type', args=[item_type.technical_name])
        post_data=self.post_data(has_targets=True, has_owners=False)
        item = self.check_post(url, post_data)

        self.check_item(item, post_data, with_targets=True)
        self.assertEqual(item.item_type, item_type)
        self.check_guidelines(item, post_data)
        self.check_snapshot_added(item, post_data)

    def test_item_with_required_field_in_custom_type_add(self):
        """Test item addition with custom content type which contains required field."""
        item_type = item_types_factories.ItemTypeFactory.create(
            desk=self.desk,
            content_schema=copy.deepcopy(VALIDATION_TEST_SCHEMA)
        )
        url = reverse('ui_item_add_with_item_type', args=[item_type.technical_name])
        post_data=self.post_data(has_targets=True, has_owners=False)
        item = self.check_post(url, post_data)

        #specific check has the custom type has no title nor body
        self.assertEqual(item.desk, self.desk)
        self.assertEqual(item.publication_dt.astimezone(self.user_timezone).date(), self.publication_dt.date())
        self.assertEqual(item.item_type, item_type)
        self.check_guidelines(item, post_data)
        session = EditSession.objects.get(item=item)
        self.assertEqual(session.version, '1.0')
        self.assertEqual(session.created_by, item.created_by)

    def test_item_with_custom_type_and_project_add(self):
        """Test item addition with custom content type and a given project(."""

        project = projects_factories.ProjectFactory.create(desk=self.desk)
        item_type = item_types_factories.ItemTypeFactory.create(desk=self.desk)
        url = reverse(
            'ui_item_add_with_item_type_and_project',
            kwargs={'item_type': item_type.technical_name, 'project_pk': project.pk}
        )
        post_data = self.post_data(has_targets=False, has_owners=False)
        item = self.check_post(url, post_data)

        self.check_item(item, post_data)
        self.assertEqual(item.item_type, item_type)
        self.assertEqual(item.project, project)

    def test_tweet_item_add(self):
        """Test tweet item add."""

        url = reverse('ui_item_add_with_item_type', kwargs={'item_type': 'twitter'})
        post_data = self.post_data(has_targets=True, has_owners=False, is_tweet=True)
        item = self.check_post(url, post_data)

        self.check_item(item, post_data, with_targets=True)
        self.check_full_datetime(item)
        self.assertEqual(item.item_type, initial_item_types.TWITTER_TYPE)
        self.check_guidelines(item, post_data)
        self.check_snapshot_added(item, post_data)

    def test_tweet_item_add_addanother(self):
        """Test create several tweets """
        twitter_type = self.desk.channel_types.get(icon=ChannelType.Icon.TWITTER)
        projects = projects_factories.ProjectFactory.create_batch(size=10, desk=self.desk)
        channels = channels_factories.ChannelFactory.create_batch(
            size=10,
            desk=self.desk,
            type=twitter_type)
        url = reverse('ui_item_add_with_item_type', kwargs={'item_type': 'twitter'})
        post_data = self.post_data(has_targets=True, has_owners=True, is_tweet=True)

        post_data.update({'addanother': True,
                          'project': projects[4].pk,
                          'channel': channels[5].pk})
        response = self.check_post_with_no_redirect(url, post_data)

        #Check item created
        item = Item.objects.get(guidelines=post_data['guidelines'])
        self.check_item(item, post_data, with_targets=True)
        self.check_full_datetime(item)
        self.assertEqual(item.item_type, initial_item_types.TWITTER_TYPE)
        self.check_guidelines(item, post_data)
        self.check_snapshot_added(item, post_data)

        #Check return form
        self.check_display_input(response, [
            'title', 'body', 'publication_date', 'publication_time', 'owners', 'addanother',
            'targets', 'channel'
        ])
        self.check_not_display_input(response,['publication_dt'])
        for (field, value) in [
                ['project', u'%s' % projects[4].pk],
                ['channel', u'%s' % channels[5].pk],
                ['owners', [u'%s' % o.pk for o in self.owners]],
                ['targets', [u'%s' % t for t in post_data['targets']]],
                ['publication_date', ''],
                ['publication_time', '']]:
            self.assertEqual(value, response.context['form'][field].data)

    def test_long_tweet_added(self):
        """Test error message is body tweet is too long"""

        url = reverse('ui_item_add_with_item_type', kwargs={'item_type': 'twitter'})
        post_data = self.post_data(has_targets=True, has_owners=False, is_tweet=True)
        post_data['body'] = u'%s' % json.dumps(prosemirror_body("x~" * 72))  # more than 280 chars
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'content_form', 'body',
                             'Contenu trop long. Twitter autorise seulement 280 signes ( 284 signes saisis)')


    def test_tweet_item_add_with_project(self):
        """Test tweet item add with project. (from the project detail page)"""

        project = projects_factories.ProjectFactory.create(desk=self.desk)
        url = reverse('ui_item_add_with_item_type_and_project', kwargs={'project_pk': project.pk,
                                                                         'item_type': 'twitter'})
        post_data =self.post_data(has_targets=False, has_owners=False, is_tweet=True)
        item = self.check_post(url, post_data)

        self.check_item(item, post_data)
        self.check_full_datetime(item)
        self.assertEqual(item.project, project)
        self.assertEqual(item.item_type, initial_item_types.TWITTER_TYPE)
        self.check_guidelines(item, post_data)

    def test_facebook_item_add(self):
        """Test facebook item add."""

        url = reverse('ui_item_add_with_item_type', kwargs={'item_type': 'facebook'})
        post_data = self.post_data(has_targets=True, has_owners=False, is_facebook=True)
        item = self.check_post(url, post_data)

        self.check_item(item, post_data, with_targets=True)
        self.check_full_datetime(item)
        self.assertEqual(item.item_type, initial_item_types.FACEBOOK_TYPE)
        self.check_guidelines(item, post_data)
        self.check_snapshot_added(item, post_data)

    def test_long_facebook_added(self):
        """Test error message is body facebook is too long"""

        url = reverse('ui_item_add_with_item_type', kwargs={'item_type': 'facebook'})
        post_data = self.post_data(has_targets=True, has_owners=False, is_facebook=True)
        post_data['body'] =  u'%s' % json.dumps(prosemirror_body("x~" * 5001))  # more than 10000 chars
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'content_form', 'body',
                             'Contenu trop long. Facebook autorise seulement 10000 signes ( 10002 signes saisis)')

    def test_facebook_item_with_project_add(self):
        """Test facebook item add."""

        project = projects_factories.ProjectFactory.create(desk=self.desk)
        url = reverse('ui_item_add_with_item_type_and_project', kwargs={'project_pk': project.pk,
                                                                         'item_type': 'facebook'})

        post_data = self.post_data(has_targets=False, has_owners=False, is_facebook=True)
        item = self.check_post(url, post_data)

        item = Item.objects.get(guidelines=post_data['guidelines'])
        self.check_item(item, post_data)
        self.assertEqual(item.item_type, initial_item_types.FACEBOOK_TYPE)
        self.check_full_datetime(item)
        self.check_snapshot_added(item, post_data)
        self.check_guidelines(item, post_data)


class ItemsUiTest(PilotAdminUserMixin, WorkflowStateTestingMixin, TestCase):
    """Test CRUD on Item objects."""
    ALLOWED_LANGUAGES = ['fr_FR', 'es_ES', 'fi_FI']

    def setUp(self):
        super(ItemsUiTest, self).setUp()
        # Keep a reference to the list view URL.
        self.main_items_list_url = reverse('ui_items_list')
        self.scope_choices = (list(zip(*Item.SCOPE_CHOICES)) + [None])[0]
        self.owners = user_factories.PilotUserFactory.create_batch(2)
        self.desk.users.add(*self.owners)

    def tearDown(self):
        # Delete all Item objects after each test.
        Item.all_the_objects.all().delete()

    @skip("Item list is now loaded through Vue.js, we should rewrite this test")
    def test_items_list(self):
        """Test the main list view."""

        items = items_factories.ConfirmedItemFactory.create_batch(size=10, desk=self.desk, owners=self.owners)

        # Test GET.
        response = self.client.get(self.main_items_list_url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(items), response.context['items_num'])
        self.assertFalse(self.desk.item_languages_enabled)
        # This triggers the `language` column display - must be hidden there
        self.assertContains(response, '<th ng-if="false">Langue</th>')

        # Testing proper `data-language-enabled` display
        d = Desk.objects.get(pk=self.desk.pk)
        d.item_languages_enabled = True
        d.save()
        response = self.client.get(self.main_items_list_url)
        self.assertEqual(len(items), response.context['items_num'])
        # This triggers the `language` column display - must be visible there
        self.assertContains(response, '<th ng-if="true">Langue</th>')

    @skip("BigFilter has been Vueified, this test should be rewritten")
    def test_big_filter_in_items_list(self):
        """Test the main list view."""

        items = items_factories.ConfirmedItemFactory.create_batch(size=10, desk=self.desk, owners=self.owners)
        channels = channels_factories.ChannelFactory.create_batch(size=10, desk=self.desk)
        projects = projects_factories.ProjectFactory.create_batch(size=10, desk=self.desk)
        targets = targets_factories.TargetFactory.create_batch(size=10, desk=self.desk)

        # Test bigfilter dropdown with desk international mode disabled
        response = self.client.get(self.main_items_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'big-filter')
        self.assertNotContains(response, '<optgroup label="Langues">')
        self.assertContains(response, '<optgroup label="Cibles">')
        for target in targets:
            self.assertContains(response, '<option value="targets={0}">{1}</option>'.format(target.pk, target.name))
        self.assertContains(response, '<optgroup label="Projets">')
        for project in projects:
            self.assertContains(response,
                                '<option value="project={0}">{1}</option>'.format(project.pk, project.name))
        self.assertContains(response, '<optgroup label="États des contenus">')
        self.assertNotContains(response, '<optgroup label="États des projets">')  # Only displayed on Calendars
        for state in self.desk.workflow_states.all():
            self.assertContains(response, '<option value="workflow_state={0}">{1}</option>'.format(state.id, state.label))
        self.assertContains(response, '<optgroup label="Canaux">')
        for channel in channels:
            self.assertContains(response, '<option value="channel={0}">{1}</option>'.format(channel.pk, channel.hierarchy))

        # Test bigfilter dropdown with desk international mode enabled
        # Desk.objects.all()[1].delete()
        d = Desk.objects.get(pk=self.desk.pk)
        d.item_languages_enabled = True
        d.allowed_languages = ['fr_FR', 'en_US', 'tr_TR']
        d.save()
        response = self.client.get(self.main_items_list_url)
        self.assertEqual(len(items), response.context['items_num'])
        # This triggers the `language` column display - must be visible there
        self.assertContains(response, '<optgroup label="Langues">')
        self.assertContains(response, '<option value="language=fr_FR">Français</option>')

    @skip("Trash item list has been moved to the main item list")
    def test_trash_items_list(self):
        """Test the trash list view."""

        items_factories.ConfirmedItemFactory.create_batch(size=7, desk=self.desk)
        items_factories.ConfirmedItemFactory.create_batch(
            size=10,
            desk=self.desk,
            in_trash=True
        )

        # Test GET.
        response = self.client.get(self.main_items_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'items/trash.html')

        self.assertFalse(self.desk.item_languages_enabled)
        # This triggers the `language` column display - must be hidden there
        self.assertContains(response, '<th ng-if="false">Langue</th>')

        # Testing proper `data-language-enabled` display
        d = Desk.objects.get(pk=self.desk.pk)
        d.item_languages_enabled = True
        d.save()
        response = self.client.get(self.main_items_list_url)
        # This triggers the `language` column display - must be visible there
        self.assertContains(response, '<th ng-if="true">Langue</th>')

    @skip("Item list is now loaded through Vue.js, we should rewrite this test")
    def test_channels_choices_are_presented_using_hierarchy_field(self):
        """Ensure that channels hierarchy is shown instead of names."""

        items = items_factories.ConfirmedItemFactory.create_batch(size=5, desk=self.desk)

        parent = channels_factories.ChannelFactory.create()
        channel = items[0].channel
        channel.parent = parent
        channel.save()

        response = self.client.get(self.main_items_list_url)
        self.assertContains(response, channel.hierarchy)

    @skip("Test obsoleted by the new Vue.js UI")
    def test_item_details(self):
        """Test the details view of an item."""
        item = items_factories.ConfirmedItemFactory.create(desk=self.desk, owners=self.owners)
        url = reverse('ui_item_details', kwargs={'item_pk': item.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(item, response.context['item'])
        self.assertEqual(item.EditSession.latest(), response.context['session'])
        self.assertNotContains(response, 'id="instant-publish-button"')  # Container to be updated via js
        self.assertContains(response, 'id="tab-informations"')  # SubMenu
        self.assertContains(response, 'id="tab-versions"')  # SubMenu
        self.assertContains(response, str(self.owners[0]))
        self.assertContains(response, str(self.owners[1]))
        self.assertContains(response, 'owner_name', count=2)

    @skip("Test obsoleted by the new Vue.js UI")
    def test_item_details_was_moved_to_trash(self):
        """Test the details view of an item when it has been moved to trash."""

        item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk,
            in_trash=True
        )
        url = reverse('ui_item_details', kwargs={'item_pk': item.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(item, response.context['item'])
        self.assertContains(response, u'a été mis à la corbeille')

    @skip("Social features disabled for now")
    def test_tweet_item_details(self):
        """Test the details view of a Tweet item."""

        item = items_factories.ConfirmedItemTweetFactory.create(desk=self.desk)
        url = reverse('ui_item_details', kwargs={'item_pk': item.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(force_str(response.context['item'].item_type.name), "Tweet")
        self.assertEqual(item, response.context['item'])
        self.assertEqual(item.EditSession.latest(), response.context['session'])
        self.assertContains(response, 'id="instant-publish-button"')  # Container to be updated via js

         # Test social log informations
        item.workflow_state = self.get_state_published()
        item.save()
        TweetLogFactory.create(item=item, tweet_id="5678", info={'favorite_count': 7, 'retweet_count': 3})
        # Test GET.
        response = self.client.get(url)
        self.assertContains(response, 'square-corners')
        self.assertContains(response, 'Voir sur twitter')
        self.assertContains(response, 'Mises en favori: 7')
        self.assertContains(response, 'Nombre de retweets: 3')

    @skip("Test obsoleted by the new Vue.js UI")
    def test_add_item_form(self):
        projects_factories.ProjectFactory.create(desk=self.desk)

        form = items_forms.AddItemForm(desk=self.desk, user=self.user)
        self.assertTrue(form.fields.get('project'))
        self.assertTrue(form.fields.get('owners'))

        form = items_forms.AddItemForm(desk=self.desk, user=self.user, hide_project=True)
        self.assertFalse(form.fields.get('project'))
        self.assertFalse(
            form.fields.get('language'))  # Must be hidden because Desk.language_enable is False by default

    @skip("Test obsoleted by the new Vue.js UI")
    def test_add_item_form_with_language_enabled(self):
        # Creating a desk with language fields enabled
        desk_language_enabled = desks_factories.DeskFactory(
            organization=self.organization,
            item_languages_enabled=True,
            allowed_languages=ItemsUiTest.ALLOWED_LANGUAGES
        )
        # Item creation form instanciation
        form = items_forms.AddItemForm(desk=desk_language_enabled, user=self.user)

        language_field = form.fields.get('language')

        # Language field is present
        self.assertTrue(language_field)

        # Allowed languages are there
        choices = language_field.choices[1:]  # Removing blank choice for comparison purpose
        self.assertEqual([el[0] for el in choices], ItemsUiTest.ALLOWED_LANGUAGES)

        # Switch off `item_languages_enabled`
        desk_language_enabled.item_languages_enabled = False
        desk_language_enabled.save()
        form = items_forms.AddItemForm(desk=desk_language_enabled, user=self.user)
        self.assertFalse(form.fields.get('language'))  # language field is not there

    @skip("Social features disabled for now")
    def test_facebook_item_details(self):
        """Test the details view of a Tweet item."""

        item = items_factories.ConfirmedItemFacebookFactory.create(desk=self.desk)
        url = reverse('ui_item_details', kwargs={'item_pk': item.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(force_str(response.context['item'].item_type.name), "Statut Facebook")
        self.assertEqual(item, response.context['item'])
        self.assertEqual(item.EditSession.latest(), response.context['session'])
        self.assertContains(response, 'id="instant-publish-button"')  # Container to be updated via js

        # Test social log informations
        item.workflow_state = self.get_state_published()
        item.save()
        FacebookLogFactory.create(
            item=item,
            status_id="1234",
            info={
                'shares': {'count': 11},
                'likes': {'summary': {'total_count': 9}}
            })
        # Test GET.
        response = self.client.get(url)
        self.assertContains(response, 'square-corners')
        self.assertContains(response, 'Voir sur facebook')
        self.assertContains(response, 'Mises en partage: 11')
        self.assertContains(response, 'Nombre de likes: 9')

    @skip("View not used anymore, to be removed")
    def test_item_versions_diff(self):
        """Test diff view of 2 versions of an item content."""

        item = items_factories.ConfirmedItemFactory.create(desk=self.desk)
        # Create 1 new version of the content.
        items_factories.EditSessionFactory.create(item=item)
        self.assertEqual(2, item.EditSession.all().count())
        left = item.EditSession.earliest()
        right = item.EditSession.latest()

        # Test GET with Django URL patterns.
        url = reverse('ui_item_versions_diff', kwargs={'item_pk': item.pk, 'left_pk': left.pk, 'right_pk': right.pk, })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(left, response.context['left'])
        self.assertEqual(right, response.context['right'])
        self.assertContains(response, '<del>')
        self.assertContains(response, '<ins>')

        # Test GET with GET parameters.
        url = '{url}?left={left_pk}&right={right_pk}'.format(
            url=reverse('ui_item_versions_diff', kwargs={'item_pk': item.pk, }),
            left_pk=left.pk,
            right_pk=right.pk
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(left, response.context['left'])
        self.assertEqual(right, response.context['right'])
        self.assertContains(response, '<del>')
        self.assertContains(response, '<ins>')

    @skip("Test obsoleted by the new Vue.js UI")
    def test_distribution_form(self):
        twitter_channel_number = 7
        facebook_channel_number = 11
        cms_channel_number = 10
        print_channel_number = 10
        total = twitter_channel_number + facebook_channel_number + cms_channel_number + print_channel_number

        channels_factories.TwitterChannelFactory.create_batch(
            twitter_channel_number,
            desk=self.desk
        )
        channels_factories.FacebookChannelFactory.create_batch(
            facebook_channel_number,
            desk=self.desk
        )
        channels_factories.ChannelFactory.create_batch(
            cms_channel_number,
            desk=self.desk,
            type__name="CMS",
        )
        channels_factories.ChannelFactory.create_batch(
            print_channel_number,
            desk=self.desk,
            type__name="Print",
        )

        item = items_factories.ConfirmedItemFactory.create(desk=self.desk, channel=None)
        item_type = item_types_factories.ItemTypeFactory.create(desk=self.desk)

        custom_item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk,
            channel=None,
            item_type=item_type
        )

        f = items_forms.DistributionItemForm(desk=self.desk, instance=item)
        # We add  1 because of the blank choice
        self.assertEqual(len(list(f.fields['channel'].choices)), total + 1)
        self.assertEqual(len(f.fields['owners'].choices), self.desk.users.count())
        f = items_forms.DistributionItemForm(desk=self.desk, instance=custom_item)
        self.assertEqual(len(list(f.fields['channel'].choices)), total + 1)

    @skip("Test obsoleted by the new Vue.js UI")
    def test_item_edit_distribution(self):
        """Test edit item distribution infos."""

        item = items_factories.ConfirmedItemFactory.create(desk=self.desk)
        url = reverse('ui_item_edit_distribution', kwargs={'item_pk': item.pk})

        publication_dt = (timezone.now() + datetime.timedelta(days=10))

        # Create an `active` project.
        project = projects_factories.ProjectFactory.create(
            desk=self.desk, state=states.STATE_ACTIVE)

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        target1 = targets_factories.TargetFactory(desk=self.desk)
        target2 = targets_factories.TargetFactory(desk=self.desk)

        post_data = {
            'project': project.pk,
            'publication_dt': publication_dt.strftime('%Y-%m-%d'),
            'targets': [target1.pk, target2.pk],
            'owners': [o.pk for o in self.owners]

        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, item.get_absolute_url())

        # Check edited Item.
        item = Item.objects.get(pk=item.pk)
        self.assertEqual(item.project, project)
        self.assertEqual(item.desk, self.desk)
        self.assertEqual(item.updated_by, self.user)

        # Checking targets. We use set to order lists.
        self.assertEqual(
            set([target.pk for target in item.targets.all()]),
            set(post_data['targets'])
        )

        # Checking owners.
        self.assertEqual(
            set([o.pk for o in item.owners.all()]),
            set(post_data['owners'])
        )

    @skip("Test obsoleted by the new Vue.js UI")
    def test_tweet_item_edit_distribution(self):
        """Test edit item distribution infos."""

        item = items_factories.ConfirmedItemTweetFactory.create(desk=self.desk)
        url = reverse('ui_item_edit_distribution', kwargs={'item_pk': item.pk})

        publication_dt = (timezone.now() + datetime.timedelta(days=10))

        # Create an `active` project.
        project = projects_factories.ProjectFactory.create(
            desk=self.desk, state=states.STATE_ACTIVE)

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        target1 = targets_factories.TargetFactory(desk=self.desk)
        target2 = targets_factories.TargetFactory(desk=self.desk)

        post_data = {
            'project': project.pk,
            'publication_date': publication_dt.strftime('%Y-%m-%d'),
            'publication_time': publication_dt.strftime('%H:%M'),
            'targets': [target1.pk, target2.pk],
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, item.get_absolute_url())

        # Check edited Item.
        item = Item.objects.get(pk=item.pk)
        self.assertEqual(item.project, project)
        self.assertEqual(item.desk, self.desk)
        self.assertEqual(item.updated_by, self.user)

        # Checking targets. We use set to order lists.
        self.assertEqual(
            set([target.pk for target in item.targets.all()]),
            set(post_data['targets'])
        )

    @skip("Test obsoleted by the new Vue.js UI")
    def test_item_edit_guidelines(self):
        """Test edit item guidelines infos."""

        item = items_factories.ConfirmedItemFactory.create(desk=self.desk)
        url = reverse('ui_item_edit_guidelines', kwargs={'item_pk': item.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        post_data = {
            'guidelines': 'New Guidelines.',
            'where': u'New Item where ünicôdé',
            'goal': u'New Item goal ünicôdé',
            'contacts': u'New Item contacts ünicôdé',
            'sources': u'New Item source ünicôdé',
            'available_pictures': bool(random.getrandbits(1)),
            'photographer_needed': bool(random.getrandbits(1)),
            'investigations_needed': bool(random.getrandbits(1)),
            'support_needed': bool(random.getrandbits(1)),
        }

        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, item.get_absolute_url())

        # Check edited Item.
        item = Item.objects.get(pk=item.pk)
        self.assertEqual(item.guidelines, post_data['guidelines'])
        self.assertEqual(item.where, post_data['where'])
        self.assertEqual(item.goal, post_data['goal'])
        self.assertEqual(item.contacts, post_data['contacts'])
        self.assertEqual(item.sources, post_data['sources'])
        self.assertEqual(item.available_pictures, post_data['available_pictures'])
        self.assertEqual(item.photographer_needed, post_data['photographer_needed'])
        self.assertEqual(item.investigations_needed, post_data['investigations_needed'])
        self.assertEqual(item.support_needed, post_data['support_needed'])

    @skip("Test obsoleted by the new Vue.js UI")
    def test_item_language_dropdown(self):
        self.desk.item_languages_enabled = True
        self.desk.allowed_languages = [lang for lang in LANGUAGES.keys()[:3]]
        self.desk.save()
        lang = LANGUAGES_CHOICES[1][0]

        item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk,
            language=lang
        )

        # Testing when item is published. Dropdown should be activated
        url_item = reverse('ui_item_details', kwargs={'item_pk': item.pk})
        response = self.client.get(url_item)
        self.assertContains(
            response,
            '<span class="item-lang dropdown-lang-spinner">{0}</span>'.format(item.get_language_abbr()))

        for language_code in LANGUAGES.keys()[:3]:  # All desk allowed_languages should be in the dropdown
            self.assertContains(response, LANGUAGES[language_code])

    @skip("Test obsoleted by the new Vue.js UI")
    def test_access_to_private_item(self):
        self.desk.private_items_enabled = True
        self.desk.save()

        owner_user = user_factories.EditorFactory.create(password='password')
        admin_user = user_factories.AdminFactory.create(password='password')
        other_user = user_factories.EditorFactory.create(password='password')
        self.desk.users.add(owner_user, admin_user, other_user)

        item = items_factories.ConfirmedItemFactory.create(desk=self.desk, owners=[owner_user], is_private=True)
        url = reverse('ui_item_details', kwargs={'item_pk': item.pk})

        # Creator can access the item
        response = self.client.get(url)
        self.assertContains(response, '<article class="ItemDetailBody__editorContainerPanel"')

        # Owner can access the item
        self.client.login(email=owner_user.email, password='password')
        response = self.client.get(url)
        self.assertContains(response, '<article class="ItemDetailBody__editorContainerPanel"')

        # Admins can access the item
        self.client.login(email=admin_user.email, password='password')
        self.assertContains(response, '<article class="ItemDetailBody__editorContainerPanel"')

        # Random guy cannot access the item
        self.client.login(email=other_user.email, password='password')
        response = self.client.get(url)
        self.assertContains(response, 'Ce contenu est privé.')
        self.assertNotContains(response, '<article class="ItemDetailBody__editorContainerPanel"')



class ItemCopyTest(ItemFormTest):

    def setUp(self):
        super(ItemCopyTest, self).setUp()
        self.target1 = targets_factories.TargetFactory(desk=self.desk)
        self.target2 = targets_factories.TargetFactory(desk=self.desk)
        self.projects = projects_factories.ProjectFactory.create_batch(size=3, desk=self.desk)
        twitter_type = self.desk.channel_types.get(icon=ChannelType.Icon.TWITTER)
        self.channels = channels_factories.ChannelFactory.create_batch(
            size=3,
            desk=self.desk,
            type=twitter_type
        )

    def post_data(self,form, content_form, item=None):
        post_data = {
            'available_pictures': form.initial['available_pictures'],
            'project': form.initial['project'],
            'channel': form.initial['channel'],
            'contacts': form.initial['contacts'],
            'goal': form.initial['goal'],
            'guidelines': form.initial['guidelines'],
            'investigations_needed': form.initial['investigations_needed'],
            'owners': [owner.pk for owner in form.initial['owners']],
            'photo_investigations_needed': form.initial['investigations_needed'],
            'photographer_needed': form.initial['photographer_needed'],
            'publication_dt': self.publication_dt.strftime('%Y-%m-%d'),
            'scope': random.choice(self.scope_choices),
            'sources': form.initial['sources'],
            'support_needed': form.initial['support_needed'],
            'targets': [target.pk for target in form.initial['targets']],
            'title': content_form.initial['title'],
            'where': form.initial['where'],
        }
        if item:
            post_data['body'] = prosemirror_body_string(prosemirror_json_to_text(item.body))
        else:
            post_data['body'] = self.body_unicode
        return post_data


    def check_forms(self, response, with_channels=True):
        form = response.context['form']
        content_form = response.context['content_form']
        self.assertTrue(isinstance(form, items_forms.AddItemForm))
        self.assertTrue(isinstance(content_form, items_forms.CopyItemContentForm))
        fields = [
            ['project', self.projects[1].pk],
            ['owners', [o.pk for o in self.owners]],
            ['targets', [self.target2.pk, self.target1.pk]]]
        if with_channels:
            fields.append(['channel',  self.channels[2].pk])
        for (field, value) in fields:
            self.assertEqual(value, form[field].value(), '{} : {!r} != {!r}'.format(field, value, form[field].value()))

    def check_publication_dt(self, response):
        form = response.context['form']
        self.assertEqual(
            self.item.publication_dt.astimezone(self.user_timezone).strftime('%d %m %Y'),
            form['publication_dt'].value().strftime('%d %m %Y')
        )

    def check_publication_date(self, response):
        form = response.context['form']
        self.assertEqual(
            self.item.publication_dt.astimezone(self.user_timezone).strftime('%d %m %Y'),
            form['publication_date'].value().strftime('%d %m %Y')
        )

    def check_publication_time(self, response):
        form = response.context['form']
        self.assertEqual(
            self.item.publication_dt.astimezone(self.user_timezone).strftime('%H:%M'),
            form['publication_time'].value()
        )

@skip("Test obsoleted by the new Vue.js UI")
class ItemsCopyFromFacebookUiTest(ItemCopyTest):
    """Test item copy from Twitter type to genral"""

    def setUp(self):
        super(ItemsCopyFromFacebookUiTest, self).setUp()
        self.previous_item()

    def previous_item(self):
        self.item = items_factories.ConfirmedItemFacebookFactory.create(
            desk=self.desk,
            project=self.projects[1],
            channel=self.channels[2],
            targets=[self.target1, self.target2],
            owners=self.owners
        )

    def test_get_to_twitter(self):
        new_item_type = initial_item_types.TWITTER_TYPE
        url = reverse('ui_item_copy', kwargs={'item_pk': self.item.pk, 'new_item_type': new_item_type})

        response = self.check_get(url)
        self.check_display_input(response, ['body', 'title', 'publication_date', 'publication_time', 'owners',
                                            'project', 'channel', 'targets'])
        self.check_not_display_input(response, ['publication_dt', 'addanother'])
        self.check_forms(response)
        self.check_publication_date(response)
        self.check_publication_time(response)

@skip("Test obsoleted by the new Vue.js UI")
class ItemsCopyWithTagsAndAsset(ItemCopyTest):

    def post_data(self,form, content_form, item, has_tags=False, has_assets=False):
        post_data = {
            'title': content_form.initial['title'],
            'body': prosemirror_body_string(prosemirror_json_to_text(item.body))
        }

        if has_tags:
            post_data['tags'] = 'foo, bar'

        if has_assets:
            post_data['assets'] = [asset.pk for asset in form.initial['assets']]

        return post_data

    def setUp(self):
        super(ItemsCopyWithTagsAndAsset, self).setUp()
        self.previous_item()

    def previous_item(self):
        assets = assets_factories.AssetFactory.create_batch(2, desk=self.desk)
        self.item = items_factories.ConfirmedItemFactory.create(desk=self.desk,
                                                                assets=assets)
        self.item.tags.add('foo')
        self.item.tags.add('bar')

    def create_copy(self, has_tags=False, has_assets=False):
        new_item_type = initial_item_types.ARTICLE_TYPE
        url = reverse('ui_item_copy', kwargs={'item_pk': self.item.pk, 'new_item_type': new_item_type})

        response = self.check_get(url)
        form = response.context['form']
        content_form = response.context['content_form']
        post_data = self.post_data(form, content_form, self.item, has_tags, has_assets)
        return self.check_post(url, post_data)


    def test_post_with_tags(self):
        copy_item = self.create_copy(has_tags=True, has_assets=False)
        self.assertEqual(2, copy_item.tags.all().count())
        for expected_tag in ['foo', 'bar']:
             self.assertTrue(expected_tag in map(lambda t: t.name, copy_item.tags.all()), '{} is not found'.format(expected_tag))

    def test_post_with_assets(self):
        copy_item = self.create_copy(has_tags=False, has_assets=True)
        self.assertEqual(2, copy_item.assets.all().count())
        for asset in copy_item.assets.all():
            self.assertEqual(2, asset.items.all().count())

@skip("Test obsoleted by the new Vue.js UI")
class ItemsCopyFromTwitterUiTest(ItemCopyTest):
    """Test item copy from Twitter type to general"""

    def setUp(self):
        super(ItemsCopyFromTwitterUiTest, self).setUp()
        self.previous_item()

    def previous_item(self):
        self.item = items_factories.ConfirmedItemTweetFactory.create(
            desk=self.desk,
            project=self.projects[1],
            channel=self.channels[2],
            targets=[self.target1, self.target2],
            owners=self.owners
        )

    def test_get_to_general(self):
        new_item_type = initial_item_types.ARTICLE_TYPE
        url = reverse('ui_item_copy', kwargs={'item_pk': self.item.pk, 'new_item_type': new_item_type})

        response = self.check_get(url)
        #Display body on copy form
        self.check_display_input(response, ['title', 'body', 'publication_dt', 'owners',
                                            'project', 'channel', 'targets', 'publication_dt'])
        self.check_not_display_input(response, ['publication_date', 'publication_time', 'addanother'])
        self.check_forms(response)
        form = response.context['form']
        self.assertEqual(
            self.item.publication_dt.astimezone(self.user_timezone).strftime('%d %m %Y %H:%M'),
            form['publication_dt'].value().strftime('%d %m %Y %H:%M')
        )

    def test_get_to_twitter(self):
        new_item_type = initial_item_types.TWITTER_TYPE
        url = reverse('ui_item_copy', kwargs={'item_pk': self.item.pk, 'new_item_type': new_item_type})

        response = self.check_get(url)
        self.check_display_input(response, ['title', 'body', 'publication_date', 'publication_time', 'owners',
                                            'project', 'channel', 'targets'])
        self.check_not_display_input(response, ['publication_dt', 'addanother'])
        self.check_forms(response)
        form = response.context['form']
        self.assertEqual(
            self.item.publication_dt.astimezone(self.user_timezone).strftime('%d %m %Y'),
            form['publication_date'].value().strftime('%d %m %Y')
        )
        self.assertEqual(
            self.item.publication_dt.astimezone(self.user_timezone).strftime('%H:%M'),
            form['publication_time'].value()
        )

    def test_get_to_facebook(self):
        new_item_type = initial_item_types.FACEBOOK_TYPE
        url = reverse('ui_item_copy', kwargs={'item_pk': self.item.pk, 'new_item_type': new_item_type})

        response = self.check_get(url)
        self.check_display_input(response, ['body', 'title', 'publication_date', 'publication_time', 'owners',
                                            'project', 'channel', 'targets'])
        self.check_not_display_input(response, ['publication_dt', 'addanother'])
        self.check_forms(response, with_channels=False)
        form = response.context['form']
        self.assertEqual(
            self.item.publication_dt.astimezone(self.user_timezone).strftime('%d %m %Y'),
            form['publication_date'].value().strftime('%d %m %Y')
        )
        self.assertEqual(
            self.item.publication_dt.astimezone(self.user_timezone).strftime('%H:%M'),
            form['publication_time'].value()
        )

    def test_post_to_general(self):
        new_item_type = initial_item_types.ARTICLE_TYPE
        url = reverse('ui_item_copy', kwargs={'item_pk': self.item.pk, 'new_item_type': new_item_type})

        response = self.check_get(url)
        form = response.context['form']
        content_form = response.context['content_form']
        post_data = self.post_data(form, content_form)

        new_item = self.check_post(url, post_data)

        # Check copied Item.
        self.assertEqual(new_item.item_type, new_item_type)

        self.check_item(new_item, post_data, with_targets=True, with_owners=True)

        self.assertEqual(new_item.channel, self.item.channel)
        self.assertEqual(new_item.desk, self.desk)
        self.assertEqual(new_item.workflow_state, self.get_state_edition_ready())
        self.assertEqual(new_item.publication_dt.astimezone(self.user_timezone).date(), self.publication_dt.date())

        self.check_guidelines(new_item, post_data)

@skip("Test obsoleted by the new Vue.js UI")
class ItemsCopyFromGeneralUiTest(ItemCopyTest):
    """Test item copy from General type to Custom with required field in content"""

    def setUp(self):
        super(ItemsCopyFromGeneralUiTest, self).setUp()
        self.previous_item()

    def previous_item(self):
        self.item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk,
            project=self.projects[1],
            channel=self.channels[2],
            targets=[self.target1, self.target2],
            owners=self.owners
        )

    def test_get_to_twitter(self):
        new_item_type = initial_item_types.TWITTER_TYPE
        url = reverse('ui_item_copy', kwargs={'item_pk': self.item.pk, 'new_item_type': new_item_type})

        response = self.check_get(url)
        self.check_display_input(response, ['title', 'publication_date', 'publication_time', 'owners',
                                            'project', 'channel', 'targets'])
        self.check_not_display_input(response, ['publication_dt'])
        form = response.context['form']
        content_form = response.context['content_form']
        self.assertTrue(isinstance(form, items_forms.AddItemForm))
        self.assertTrue(isinstance(content_form, items_forms.CopyItemContentForm))
        for (field, value) in [
                ['project', self.projects[1].pk],
                ['channel',  self.channels[2].pk],
                ['owners', [o.pk for o in self.owners]],
                ['targets', [self.target2.pk, self.target1.pk]]]:
            self.assertEqual(value, form[field].value(), '{} : {!r} != {!r}'.format(field, value, form[field].value()))
        self.assertEqual(
            self.item.publication_dt.astimezone(self.user_timezone).strftime('%d %m %Y'),
            form['publication_date'].value().strftime('%d %m %Y')
        )
        # The time should not be set
        self.assertEqual(None, form['publication_time'].value())


    def test_post_to_custom(self):
        """Test copy success even if some required data in content_form are not set"""
        item_type = item_types_factories.ItemTypeFactory.create(
            desk=self.desk,
            content_schema=copy.deepcopy(VALIDATION_TEST_SCHEMA)
        )
        new_item_type = item_type.technical_name
        url = reverse('ui_item_copy', kwargs={'item_pk': self.item.pk, 'new_item_type': new_item_type})
        response = self.check_get(url)
        form = response.context['form']
        content_form = response.context['content_form']
        post_data = self.post_data(form, content_form)

        new_item = self.check_post(url, post_data)
        self.assertEqual(new_item.item_type.technical_name, new_item_type)

class ItemsModificationTest(ItemCopyTest):

    def check_snapshot_added(self, item):
        sessions = EditSession.objects.all()
        self.assertEqual(2, sessions.count())
        self.assertEqual(['1.1', '1.0'], map(lambda x: x.version, sessions))

    def check_modify_item(self, post_data, modified_item, new_item_type):
        self.assertEqual(modified_item.item_type, new_item_type)
        self.check_item(modified_item, post_data, with_targets=True, with_owners=True, check_body=False)

        self.assertEqual(modified_item.pk, self.item.pk)
        self.assertEqual(modified_item.content['body'], self.item.content['body'])

        self.assertEqual(modified_item.channel, self.item.channel)
        self.assertEqual(modified_item.desk, self.desk)
        self.assertEqual(modified_item.workflow_state, self.item.workflow_state)
        self.assertEqual(modified_item.publication_dt.astimezone(self.user_timezone).date(), self.publication_dt.date())

        self.check_guidelines(modified_item, post_data)
        self.check_snapshot_added(modified_item)


@skip("Test obsoleted by the new Vue.js UI")
class ItemsModificationFromTwitterUiTest(ItemsModificationTest):

    def setUp(self):
        super(ItemsModificationFromTwitterUiTest, self).setUp()
        self.previous_item()

    def previous_item(self):
        self.item = items_factories.ConfirmedItemTweetFactory.create(
            desk=self.desk,
            project=self.projects[1],
            channel=self.channels[2],
            targets=[self.target1, self.target2],
            owners=self.owners
        )

    def test_get_to_general(self):
        new_item_type = initial_item_types.ARTICLE_TYPE
        url = reverse('ui_item_types_edit', kwargs={'item_pk': self.item.pk, 'new_item_type': new_item_type})

        response = self.check_get(url)
        #body is hidden
        self.check_display_input(response, ['title', 'body', 'publication_dt', 'owners',
                                            'project', 'channel', 'targets'])
        self.check_not_display_input(response, ['publication_date', 'publication_time', 'addanother'])
        self.check_forms(response)
        self.check_publication_dt(response)

    def test_get_to_facebook(self):
        new_item_type = initial_item_types.FACEBOOK_TYPE
        url = reverse('ui_item_types_edit', kwargs={'item_pk': self.item.pk, 'new_item_type': new_item_type})

        response = self.check_get(url)
        #body is hidden
        self.check_display_input(response, ['title', 'body', 'publication_date', 'publication_time', 'owners',
                                            'project','channel',  'targets'])
        self.check_not_display_input(response, ['publication_dt', 'addanother'])
        self.check_forms(response, with_channels=False)

        self.check_publication_date(response)
        self.check_publication_time(response)

    def test_post_to_general(self):
        new_item_type = initial_item_types.ARTICLE_TYPE
        url = reverse('ui_item_types_edit', kwargs={'item_pk': self.item.pk, 'new_item_type': new_item_type})

        response = self.check_get(url)
        form = response.context['form']
        content_form = response.context['content_form']

        post_data = self.post_data(form, content_form, self.item)

        modified_item = self.check_post(url, post_data)
        self.check_modify_item(post_data, modified_item, new_item_type)

@skip("Test obsoleted by the new Vue.js UI")
class ItemsModificationFromGeneralUiTest(ItemsModificationTest):

    def setUp(self):
        super(ItemsModificationFromGeneralUiTest, self).setUp()
        self.previous_item()

    def previous_item(self):
        self.item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk,
            project=self.projects[1],
            channel=self.channels[2],
            targets=[self.target1, self.target2],
            owners=self.owners
        )

    def test_get_to_twitter(self):
        new_item_type = initial_item_types.TWITTER_TYPE
        url = reverse('ui_item_types_edit', kwargs={'item_pk': self.item.pk, 'new_item_type': new_item_type})

        response = self.check_get(url)
        self.check_display_input(response, ['title', 'body', 'publication_date', 'publication_time', 'owners',
                                            'project', 'channel', 'targets'])
        self.check_not_display_input(response, ['publication_dt', 'addanother'])
        self.check_forms(response)
        form = response.context['form']
        self.assertEqual(
            self.item.publication_dt.astimezone(self.user_timezone).strftime('%d %m %Y'),
            form['publication_date'].value().strftime('%d %m %Y')
        )
        # The time should not be set
        self.assertEqual(None, form['publication_time'].value())

    def test_post_to_twitter(self):
        new_item_type = initial_item_types.ARTICLE_TYPE
        url = reverse('ui_item_types_edit', kwargs={'item_pk': self.item.pk, 'new_item_type': new_item_type})

        response = self.check_get(url)
        form = response.context['form']
        content_form = response.context['content_form']
        post_data = self.post_data(form, content_form, self.item)

        modify_item = self.check_post(url, post_data)

        # Check copied Item.
        self.assertEqual(modify_item.item_type, new_item_type)

        self.check_item(modify_item, post_data, with_targets=True, with_owners=True, check_body=False)

        self.assertEqual(modify_item.content['body'], self.item.content['body'])

        self.assertEqual(modify_item.channel, self.item.channel)
        self.assertEqual(modify_item.desk, self.desk)
        self.assertEqual(modify_item.workflow_state, self.item.workflow_state)
        self.assertEqual(modify_item.publication_dt.astimezone(self.user_timezone).date(), self.publication_dt.date())

        self.check_guidelines(modify_item, post_data)

@skip("Test obsoleted by the new Vue.js UI")
class ItemsUiOldTest(ItemFormTest):

    def setUp(self):
        super(ItemsUiOldTest, self).setUp()
        # Keep a reference to the list view URL.
        self.main_items_list_url = reverse('ui_items_list')
        self.scope_choices = (list(zip(*Item.SCOPE_CHOICES)) + [None])[0]


    def test_item_copy_to_twitter_type(self):
        """Test copy item to a twitter type item."""

        target1 = targets_factories.TargetFactory(desk=self.desk)
        target2 = targets_factories.TargetFactory(desk=self.desk)

        item = items_factories.ConfirmedItemFactory.create(desk=self.desk, targets=[target1, target2])

        new_item_type = initial_item_types.TWITTER_TYPE
        url = reverse('ui_item_copy', kwargs={'item_pk': item.pk, 'new_item_type': new_item_type})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        content_form = response.context['content_form']
        self.assertTrue(isinstance(form, items_forms.AddItemForm))
        self.assertTrue(isinstance(content_form, items_forms.CopyItemContentForm))

        user_timezone = pytz.timezone('Europe/Paris')
        publication_dt = (timezone.now() + datetime.timedelta(days=10))

        # Test POST.
        post_data = {
            'project': form.initial['project'],
            'title': content_form.initial['title'],
            'body': prosemirror_body_string(prosemirror_json_to_text(item.body)),
            'publication_date': publication_dt.strftime('%Y-%m-%d'),
            'publication_time': publication_dt.strftime('%H:%M'),
            'guidelines': form.initial['guidelines'],
            'targets': [target.pk for target in form.initial['targets']],

        }

        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)

        # Check copied Item.
        new_item = Item.objects.latest('created_at')
        self.assertRedirects(response, reverse('ui_item_details', args=[new_item.pk]))
        self.assertEqual(new_item.item_type, new_item_type)
        self.assertEqual(new_item.guidelines, item.guidelines)
        self.assertEqual(new_item.desk, self.desk)
        self.assertEqual(new_item.content['body'], item.content['body'])
        self.assertEqual(new_item.workflow_state, self.get_state_edition_ready())
        self.assertEqual(
            new_item.publication_dt.astimezone(user_timezone).strftime('%d %m %Y %H:%H'),
            publication_dt.strftime('%d %m %Y %H:%H')
        )

        # Checking targets. We use set to order lists.
        self.assertEqual(
            set([target.pk for target in item.targets.all()]),
            set(post_data['targets'])
        )

    def test_item_copy_to_custom_type(self):

        """Test copy item to a custom type item."""

        custom_type = item_types_factories.ItemTypeFactory.create(desk=self.desk)

        item = items_factories.ConfirmedItemFactory.create(desk=self.desk)

        url = reverse('ui_item_copy', kwargs={
            'item_pk': item.pk,
            'new_item_type': 'ctype-{0}'.format(custom_type.pk)
        })

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        content_form = response.context['content_form']
        self.assertTrue(isinstance(form, items_forms.AddItemForm))
        self.assertTrue(isinstance(content_form, items_forms.CopyItemContentForm))

        publication_dt = (timezone.now() + datetime.timedelta(days=10))

        # Test POST.
        post_data = {
            'project': form.initial['project'],
            'title': content_form.initial['title'],
            'body': prosemirror_body_string(prosemirror_json_to_text(item.body)),
            'publication_dt': publication_dt.strftime('%Y-%m-%d'),
            'guidelines': form.initial['guidelines'],

        }

        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        new_item = Item.objects.latest('created_at')
        self.assertRedirects(response, reverse('ui_item_details', args=[new_item.pk]))

        # Check edited Item.
        self.assertNotEqual(new_item.pk, item.pk)
        self.assertEqual(new_item.item_type, custom_type)
        self.assertEqual(new_item.guidelines, item.guidelines)
        self.assertEqual(new_item.desk, self.desk)
        self.assertEqual(new_item.workflow_state, self.get_state_edition_ready())

    def test_item_copy_from_custom_type(self):
        """Test copy item to a static type item."""

        custom_type = item_types_factories.ItemTypeFactory.create(desk=self.desk)

        item = items_factories.ConfirmedItemFactory.create(desk=self.desk)

        item.item_type = custom_type
        item.save()

        new_item_type = initial_item_types.ARTICLE_TYPE
        url = reverse('ui_item_copy', kwargs={
            'item_pk': item.pk,
            'new_item_type': new_item_type,
        })

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        content_form = response.context['content_form']
        self.assertTrue(isinstance(form, items_forms.AddItemForm))
        self.assertTrue(isinstance(content_form, items_forms.CopyItemContentForm))

        publication_dt = (timezone.now() + datetime.timedelta(days=10))

        # Test POST.
        post_data = {
            'project': form.initial['project'],
            'title': content_form.initial['title'],
            'body': prosemirror_body_string(prosemirror_json_to_text(item.body)),
            'publication_dt': publication_dt.strftime('%Y-%m-%d'),
            'guidelines': form.initial['guidelines'],

        }

        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        new_item = Item.objects.latest('created_at')
        self.assertRedirects(response, reverse('ui_item_details', args=[new_item.pk]))

        # Check edited Item.
        self.assertNotEqual(new_item.pk, item.pk)
        self.assertEqual(new_item.item_type, initial_item_types.ARTICLE_TYPE)
        self.assertEqual(new_item.item_type, None)
        self.assertEqual(new_item.guidelines, item.guidelines)
        self.assertEqual(new_item.desk, self.desk)
        self.assertEqual(new_item.workflow_state, self.get_state_edition_ready())

    def test_item_edit_item_type(self):
        """Test edit item to a general type item."""
        target1 = targets_factories.TargetFactory(desk=self.desk)
        target2 = targets_factories.TargetFactory(desk=self.desk)

        item = items_factories.ConfirmedItemFactory.create(desk=self.desk, targets=[target1, target2])

        new_item_type = initial_item_types.ARTICLE_TYPE
        url = reverse('ui_item_types_edit', kwargs={'item_pk': item.pk, 'new_item_type': new_item_type})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        content_form = response.context['content_form']
        self.assertTrue(isinstance(form, items_forms.AddItemForm))
        self.assertTrue(isinstance(content_form, items_forms.CopyItemContentForm))

        user_timezone = pytz.timezone('Europe/Paris')
        publication_dt = (timezone.now() + datetime.timedelta(days=10))

        # Test POST.
        post_data = {
            'channel': form.initial['channel'],
            'project': form.initial['project'],
            'title': content_form.initial['title'],
            'body': prosemirror_body_string(prosemirror_json_to_text(item.body)),
            'publication_dt': publication_dt.strftime('%Y-%m-%d'),
            'guidelines': form.initial['guidelines'],
            'targets': [target.pk for target in form.initial['targets']],
            'where': form.initial['where'],
            'goal': form.initial['goal'],
            'contacts': form.initial['contacts'],
            'sources': form.initial['sources'],
            'available_pictures': form.initial['available_pictures'],
            'photographer_needed': form.initial['photographer_needed'],
            'investigations_needed': form.initial['investigations_needed'],
            'support_needed': form.initial['support_needed'],
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_item_details', args=[item.pk]))

        # Check copied Item.
        new_item = Item.objects.latest('created_at')

        # Items are the same
        self.assertEqual(new_item.pk, item.pk)
        self.assertEqual(new_item.item_type, new_item_type)

        self.assertEqual(new_item.channel, item.channel)
        self.assertEqual(new_item.desk, self.desk)
        self.assertEqual(new_item.workflow_state, item.workflow_state)
        self.assertEqual(new_item.body, item.body)
        self.assertEqual(new_item.publication_dt.astimezone(user_timezone).date(), publication_dt.date())

        # Guidelines
        self.assertEqual(new_item.guidelines, item.guidelines)
        self.assertEqual(item.where, post_data['where'])
        self.assertEqual(item.goal, post_data['goal'])
        self.assertEqual(item.contacts, post_data['contacts'])
        self.assertEqual(item.sources, post_data['sources'])
        self.assertEqual(item.available_pictures, post_data['available_pictures'])
        self.assertEqual(item.photographer_needed, post_data['photographer_needed'])
        self.assertEqual(item.investigations_needed, post_data['investigations_needed'])
        self.assertEqual(item.support_needed, post_data['support_needed'])

        # Checking targets. We use set to order lists.
        self.assertEqual(
            set([target.pk for target in item.targets.all()]),
            set(post_data['targets'])
        )

        # A new EditSession is always added
        session = item.last_session
        self.assertEqual(session.version, '1.0')

    def test_change_item_type(self):
        """Test edit item to a facebook or twitter type item."""

        item = items_factories.ConfirmedItemFactory.create(desk=self.desk, owners=self.owners)

        # Get on edition to facebook
        fb_item_type = initial_item_types.FACEBOOK_TYPE
        fb_url = reverse('ui_item_types_edit', kwargs={'item_pk': item.pk, 'new_item_type': fb_item_type})
        response = self.client.get(fb_url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        content_form = response.context['content_form']
        self.assertTrue(isinstance(form, items_forms.AddItemForm))
        self.assertTrue(isinstance(content_form, items_forms.CopyItemContentForm))

        # Get on edition to twitter
        tw_item_type = initial_item_types.TWITTER_TYPE
        tweet_url = reverse('ui_item_types_edit', kwargs={'item_pk': item.pk, 'new_item_type': tw_item_type})
        response = self.client.get(tweet_url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        content_form = response.context['content_form']
        self.assertTrue(isinstance(form, items_forms.AddItemForm))
        self.assertTrue(isinstance(content_form, items_forms.CopyItemContentForm))

        # user_timezone = pytz.timezone('Europe/Paris')
        publication_dt = (timezone.now() + datetime.timedelta(days=10))

        post_data = {
            'channel': form.initial['channel'],
            'project': form.initial['project'],
            'title': content_form.initial['title'],
            'body': prosemirror_body_string(prosemirror_json_to_text(item.body)),
            'publication_date': publication_dt.strftime('%Y-%m-%d'),
            'publication_time': publication_dt.strftime('%H:%M'),
            'guidelines': form.initial['guidelines'],
            'targets': [target.pk for target in form.initial['targets']],
            'where': form.initial['where'],
            'goal': form.initial['goal'],
            'contacts': form.initial['contacts'],
            'sources': form.initial['sources'],
            'available_pictures': form.initial['available_pictures'],
            'photographer_needed': form.initial['photographer_needed'],
            'investigations_needed': form.initial['investigations_needed'],
            'support_needed': form.initial['support_needed'],
        }

        # Test POST to facebook
        response = self.client.post(fb_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_item_details', args=[item.pk]))

        # Check copied Item.
        new_item = Item.objects.latest('created_at')

        # Items are the same
        self.assertEqual(new_item.pk, item.pk)
        self.assertEqual(new_item.item_type, fb_item_type)
        self.assertEqual(new_item.body, item.body)

        # Test POST to twitter
        response = self.client.post(tweet_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_item_details', args=[item.pk]))

        # Check copied Item.
        new_item = Item.objects.latest('created_at')

        # Items are the same
        self.assertEqual(new_item.pk, item.pk)
        self.assertEqual(new_item.item_type, tw_item_type)
        self.assertEqual(new_item.body, item.body)

    def test_item_edit_tags(self):
        """Test edit item tags."""

        item = items_factories.ConfirmedItemFactory.create(desk=self.desk)
        url = reverse('ui_item_edit_tags', kwargs={'item_pk': item.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        post_data = {
            'tags': 'tag1, tag2, tag3',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, item.get_absolute_url())

        # Check edited Item.
        item = Item.objects.get(pk=item.pk)
        self.assertEqual(3, item.tags.all().count())
        for tag in ['tag1', 'tag2', 'tag3']:
            self.assertEqual(1, item.tags.filter(name__exact=tag).count())

    def test_item_put_in_trash(self):
        """Test item put in trash."""

        item = items_factories.ConfirmedItemFactory.create(desk=self.desk)
        url = reverse('ui_item_put_in_trash', kwargs={'item_pk': item.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Veuillez confirmer que vous souhaitez mettre ce contenu à la corbeille")
        self.assertContains(response, reverse('ui_item_details', args=[item.pk]))
        self.assertTemplateUsed(response, 'items/item/put_in_trash.html')

        # Test POST.
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.main_items_list_url)

        # The Item should have been put in trash thus not visible in main list.
        self.assertEqual(Item.objects.all().count(), 0)
        # But it is in trash list.
        self.assertEqual(Item.in_trash_objects.all().count(), 1)

        # Checking activity
        latest_activity = Activity.objects.latest('created_at')
        self.assertEqual(latest_activity.desk, self.desk)
        self.assertEqual(latest_activity.actor, self.user)
        self.assertEqual(latest_activity.verb, Activity.VERB_PUT_IN_TRASH)

    def test_item_restore_from_trash(self):
        """Test item restore from trash."""

        item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk,
            in_trash=True
        )
        url = reverse('ui_item_restore_from_trash', kwargs={'item_pk': item.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Veuillez confirmer que vous souhaitez restaurer ce contenu")
        self.assertContains(response, reverse('ui_item_details', args=[item.pk]))
        self.assertTemplateUsed(response, 'items/item/restore_item_from_trash.html')

        # Test POST.
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.main_items_list_url)

        # The Item should have been restored from the trash thus  visible in main list.
        self.assertEqual(Item.objects.all().count(), 1)
        # But it is no more in trash list.
        self.assertEqual(Item.in_trash_objects.all().count(), 0)

        # Checking activity
        latest_activity = Activity.objects.latest('created_at')
        self.assertEqual(latest_activity.desk, self.desk)
        self.assertEqual(latest_activity.actor, self.user)
        self.assertEqual(latest_activity.verb, Activity.VERB_RESTORED_FROM_TRASH)

    def test_item_hide(self):
        """Test item hiding aka fake delete."""

        item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk
        )
        url = reverse('ui_item_hide', kwargs={'item_pk': item.pk})

        # Test GET.
        response = self.client.get(url)
        # Item must be in trash, transition from visible to hidden is forbidden
        self.assertEqual(response.status_code, 404)

        item.put_in_trash()
        # Test GET.
        response = self.client.get(url)
        self.assertContains(response, "Veuillez confirmer que vous souhaitez supprimer ce contenu définitivement")
        self.assertContains(response, reverse('ui_item_details', args=[item.pk]))
        self.assertTemplateUsed(response, 'items/item/hide_item.html')

        # Test POST.
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.main_items_list_url)

        # The Item should have been removed from the trash and not visible in main list.
        self.assertEqual(Item.objects.all().count(), 0)
        # It is no more in trash list.
        self.assertEqual(Item.in_trash_objects.all().count(), 0)

        self.assertEqual(Item.all_the_objects.filter(hidden=True).count(), 1)

        # Checking activity
        latest_activity = Activity.objects.latest('created_at')
        self.assertEqual(latest_activity.desk, self.desk)
        self.assertEqual(latest_activity.actor, self.user)
        self.assertEqual(latest_activity.verb, Activity.VERB_HIDDEN)

    def test_item_hide_forbidden_for_non_admin(self):
        """Test item hiding is forbidden when user is not an admin"""

        item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk
        )
        item.put_in_trash()
        url = reverse('ui_item_hide', kwargs={'item_pk': item.pk})
        self.user.permission = PERMISSION_EDITORS
        self.user.save()
        # Test GET.

        response = self.client.get(url)
        # Item must be in trash, transition from visible to hidden is forbidden
        self.assertEqual(response.status_code, 404)

    def test_item_history(self):
        """Test the history view of an item."""

        item = items_factories.ConfirmedItemFactory.create(
            desk=self.desk
        )

        session_type = ContentType.objects.get(model='item')

        # Create 2 versions.
        item.put_in_trash(user=self.user)
        item.restore_from_trash(user=self.user)

        url = reverse('ui_item_history', kwargs={'item_pk': item.pk, })

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Since we interacted two times with the item we have two activities
        url_api = reverse('activity_api_list')
        url_api_queryparam = '{0}?object_type={1}&object_id={2}&page=1'.format(url_api,
                                                                               session_type.pk,
                                                                               item.pk)
        response_api = json.loads(self.client.get(url_api_queryparam).content)
        self.assertEquals(2, response_api['count'])

    def test_item_history_when_on_guideline_update(self):
        """Test the history view of an item."""

        create_url = reverse('ui_item_add')

        publication_dt = (timezone.now() + datetime.timedelta(days=10))

        # Test GET.
        response = self.client.get(create_url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        post_data = {
            'title': u'Item title ünicôdé',
            'guidelines': u'Item guidelines ünicôdé',
            'publication_dt': publication_dt.strftime('%Y-%m-%d'),
            'body': prosemirror_body_string(u'Item content ünicôdé'),
            'where': u'Item where ünicôdé',
            'goal': u'Item goal ünicôdé',
            'contacts': u'Item contacts ünicôdé',
            'sources': u'Item source ünicôdé',
            'available_pictures': bool(random.getrandbits(1)),
            'photographer_needed': bool(random.getrandbits(1)),
            'investigations_needed': bool(random.getrandbits(1)),
            'support_needed': bool(random.getrandbits(1)),
        }

        response = self.client.post(create_url, data=post_data)

        item = Item.objects.get(guidelines=post_data['guidelines'])
        session_type = ContentType.objects.get(model='item')

        # Test POST.
        post_data = {
            'guidelines': 'New Guidelines.',
            'where': u'New Item where ünicôdéd',
            'goal': u'New Item goal ünicôdéd',
            'contacts': u'New Item contacts ünicôdé',
            'sources': u'New Item source ünicôdé',
            'available_pictures': bool(random.getrandbits(1)),
            'photographer_needed': bool(random.getrandbits(1)),
            'investigations_needed': bool(random.getrandbits(1)),
            'support_needed': bool(random.getrandbits(1)),
        }

        edit_guidelines_url = reverse('ui_item_edit_guidelines', kwargs={'item_pk': item.pk})

        response = self.client.post(edit_guidelines_url, data=post_data)
        url = reverse('ui_item_history', kwargs={'item_pk': item.pk, })

        # Test GET.
        response = self.client.get(url)

        # Test POST.
        post_data = {
            'guidelines': 'New Guidelinesd.',
            'where': u'New Item where ünicôdé',
            'goal': u'New Item goal ünicôdé',
            'contacts': u'New Item contacts ünicôdé',
            'sources': u'New Item source ünicôdé',
            'available_pictures': bool(random.getrandbits(1)),
            'photographer_needed': bool(random.getrandbits(1)),
            'investigations_needed': bool(random.getrandbits(1)),
            'support_needed': bool(random.getrandbits(1)),
        }

        response = self.client.post(edit_guidelines_url, data=post_data)
        url = reverse('ui_item_history', kwargs={'item_pk': item.pk, })

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Since we interacted two times with the item we have 3 activities
        url_api = reverse('activity_api_list')
        url_api_queryparam = '{0}?object_type={1}&object_id={2}&page=1'.format(url_api,
                                                                               session_type.pk,
                                                                               item.pk)
        response_api = json.loads(self.client.get(url_api_queryparam).content)
        self.assertEquals(3, response_api['count'])

    def test_items_perms_from_another_desk(self):
        """Test items perms."""

        # Create another desk for another user.
        other_desk = desks_factories.DeskFactory.create()

        # Create an item related to the other desk.
        other_item = items_factories.ConfirmedItemFactory.create(
            desk=other_desk
        )

        # Test list, it should be empty because the logged user has no items.
        response = self.client.get('/api/items/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(0, response.json()['count'])

        # Test read perms. The other item should not be accessible.
        url = reverse(API_ITEMS_DETAIL_URL, kwargs={'pk': other_item.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # Test delete perms. The other item should not be accessible.
        url = reverse('ui_item_put_in_trash', kwargs={'item_pk': other_item.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

        self.client.logout()

        # Log the other user in.
        self.client.login(email=other_desk.created_by.email, password='password')

        # The other user can read the item.
        url = reverse(API_ITEMS_DETAIL_URL, kwargs={'pk': other_item.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # The other user can delete the item.
        url = reverse('ui_item_put_in_trash', kwargs={'item_pk': other_item.pk})
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 302)

        self.client.logout()
