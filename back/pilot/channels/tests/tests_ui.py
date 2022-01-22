import itertools
import json
from unittest import skip

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from mock import patch

from pilot.projects.tests import factories as projects_factories
from pilot.channels.tests import factories as channels_factories
from pilot.pilot_users.tests import factories as user_factories
from pilot.integrations.tests import factories as api_factories
from pilot.utils.selenium_test import SeleniumTest
from pilot.utils.test import PilotRestrictedEditorUserMixin, \
    PilotEditorUserMixin


def fake_api(*arg, **kwargs):
    return True

class ChannelsUiTest(SeleniumTest):

    def setUp(self):
        super(ChannelsUiTest, self).setUp()
        # Keep a reference to the list view URL.
        self.channels_list_url = reverse('ui_channels_list')
        self.api_channels_list_url = reverse('api_channels_list')

    def tearDown(self):
        super(ChannelsUiTest, self).tearDown()
        # Delete all Channel objects after each test.
        Channel.objects.all().delete()

    def test_channels_list(self):
        """Test channels list."""

        # Test GET.
        response = self.client.get(self.channels_list_url)
        self.assertEqual(response.status_code, 200)
        # Css class whose purpose is to test the add channel button presence
        # Restricted editors can't add channels so they don't need this button
        self.assertContains(response, "tst__channel-add")

    def test_channels_detail(self):
        """Test channel detail page."""
        owner_1 = user_factories.PilotUserFactory()
        owner_2 = user_factories.PilotUserFactory()
        channel = channels_factories.ChannelFactory.create(desk=self.desk)
        channel.owners.add(owner_1, owner_2)
        rejected_project = projects_factories.ProjectFactory.create(

            desk=self.desk,
            state=states.STATE_REJECTED
        )
        active_projects = projects_factories.ProjectFactory.create_batch(size=10, desk=self.desk)
        closed_projects = projects_factories.ProjectFactory.create_batch(
            size=10,
            desk=self.desk,
            state=states.STATE_CLOSED
        )
        idea_projects = projects_factories.ProjectFactory.create_batch(
            size=10,
            desk=self.desk,
            state=states.STATE_IDEA
        )
        for project in Project.objects.all():
            project.channels.add(channel)
            project.save()

        # Test GET.
        response = self.client.get(reverse('ui_channel_detail', args=[channel.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.count(), 31)
        self.assertContains(response, channel.name)
        self.assertContains(response, "tst__projects-list")

        # Admin can edit channels or delete them so they need theses buttons
        self.assertContains(response, "tst__channel-delete")
        self.assertContains(response, "tst__channel-edit")

        # Each project whose state is not `rejected` must be on the page
        for project in itertools.chain(active_projects, closed_projects, idea_projects):
            self.assertContains(response, project.name)

        for project in active_projects:
            self.assertContains(response, project.get_absolute_url())

        for project in idea_projects:
            self.assertContains(response, project.get_absolute_url())

        self.assertNotContains(response, rejected_project.name)
        self.assertNotContains(response, "Ce canal n'a pas de responsable pour le moment")
        self.assertContains(response, owner_1.username)
        self.assertContains(response, owner_2.username)

        channel_with_no_projects = channels_factories.ChannelFactory.create(desk=self.desk)
        # Test GET.
        response = self.client.get(reverse('ui_channel_detail', args=[channel_with_no_projects.pk]))
        self.assertNotContains(response, '<div class="list-group tst__projects-list">')
        self.assertContains(response, "Ce canal n'a pas de responsable pour le moment")

    @skip("View obsoleted by the new Vue.js UI")
    def test_channel_add(self):
        """Test channel add."""
        owner_1 = user_factories.PilotUserFactory()
        owner_2 = user_factories.PilotUserFactory()
        self.desk.users.add(owner_1, owner_2)  # They need to belong to the same desk
        publisher_1 = user_factories.PilotUserFactory()
        publisher_2 = user_factories.PilotUserFactory()
        self.desk.users.add(publisher_1, publisher_2)  # They need to belong to the same desk

        url = reverse('ui_channel_add')

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        twitter_type = self.desk.channel_types.get(icon=ChannelType.Icon.TWITTER)

        # Test POST.
        post_data = {
            'type': twitter_type.id,
            'owners': [owner_1.pk, owner_2.pk, ],
            'name': 'Channél ùn',
            'description': 'Channel lorem ipsum dolor sit amet.',
            'color': 'ff0000',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.channels_list_url)

        # Check added Channel.
        channel = Channel.objects.get(name=post_data['name'])

        self.assertEqual(channel.desk, self.desk)

        # Check owners
        self.assertEqual(channel.owners.count(), 2)
        self.assertTrue(owner_1 in channel.owners.all())
        self.assertTrue(owner_2 in channel.owners.all())

        # The just added Channel must appears in the channels list.
        response = self.client.get(self.api_channels_list_url)
        data = json.loads(response.content)
        self.assertEquals(channel.name, data[0]['name'])

        twitter_type = self.desk.channel_types.get(icon=ChannelType.Icon.TWITTER)

        # Test POST with empty M
        post_data = {
            'type': twitter_type.id,
            'name': 'Channél deux',
            'description': 'Channel lorem ipsum dolor sit amet.',
            'color': 'ff0000',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        channel = Channel.objects.get(name=post_data['name'])

    def test_channel_edit(self):
        """Test channel edit."""
        owner_1 = user_factories.PilotUserFactory()
        owner_2 = user_factories.PilotUserFactory()
        self.desk.users.add(owner_1, owner_2)  # They need to belong to the same desk

        publisher_1 = user_factories.PilotUserFactory()
        publisher_2 = user_factories.PilotUserFactory()
        self.desk.users.add(publisher_1, publisher_2)  # They need to belong to the same desk

        channel = channels_factories.ChannelFactory.create(desk=self.desk)
        url = reverse('ui_channel_edit', kwargs={'channel_pk': channel.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        post_data = {
            'type': channel.type,
            'owners': [owner_1.pk, owner_2.pk],
            'name': 'New Name',
            'description': channel.description
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_channel_detail', kwargs={'channel_pk': channel.pk, }))

        # Check updated Channel.
        channel = Channel.objects.get(pk=channel.pk)
        self.assertEqual(channel.name, post_data['name'])

        # Check owners
        self.assertEqual(channel.owners.count(), 2)
        self.assertTrue(owner_1 in channel.owners.all())
        self.assertTrue(owner_2 in channel.owners.all())
        self.assertEqual(channel.updated_by, self.user)

    def test_channel_close(self):
        """Test channel close."""

        channel = channels_factories.ChannelFactory.create(desk=self.desk)
        url = reverse('ui_channel_close_or_delete', kwargs={'channel_pk': channel.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        response = self.client.post(url, data={'action': 'close', })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_channel_detail', kwargs={'channel_pk': channel.pk, }))

        # The Channel should have been closed but should remain in the channels list.
        response = self.client.get(self.api_channels_list_url)
        channel = Channel.objects.get(pk=channel.pk)
        data = json.loads(response.content)
        self.assertEquals(channel.name, data[0]['name'])
        self.assertEqual(channel.state, states.STATE_CLOSED)
        self.assertEqual(channel.updated_by, self.user)

    def test_channel_delete(self):
        """Test channel delete."""

        channel = channels_factories.ChannelFactory.create(desk=self.desk)
        url = reverse('ui_channel_close_or_delete', kwargs={'channel_pk': channel.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        response = self.client.post(url, data={'action': 'delete', })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.channels_list_url)

        # The Channel should have been deleted.
        self.assertEqual(Channel.objects.all().count(), 0)

    def test_channel_history(self):
        """Test the history view of a channel."""

        channel = channels_factories.ChannelFactory.create(desk=self.desk)

        channel_content_type = ContentType.objects.get(model='channel')

        # Fire up browser and log in
        self.browser.get('%s%s' % (self.live_server_url, '/'))
        username_input = self.browser.find_element_by_name('username')
        username_input.send_keys(self.user.email)
        password_input = self.browser.find_element_by_name('password')
        password_input.send_keys('password')
        self.browser.find_element_by_tag_name('button').click()

        # Change channel title
        url = reverse('ui_channel_edit', kwargs={'channel_pk': channel.pk})
        self.browser.get('%s%s' % (self.live_server_url, url))
        # For some reason the browser doesn't hear the first time, let's repeat it .
        self.browser.get('%s%s' % (self.live_server_url, url))
        self.assertIn('Pilot - Canaux - Modifier un canal', self.browser.title)

        self.browser.find_element_by_id('id_name').send_keys('New title')
        self.browser.find_element_by_tag_name('button').click()

        # Change channel title once again
        url = reverse('ui_channel_edit', kwargs={'channel_pk': channel.pk})
        self.browser.get('%s%s' % (self.live_server_url, url))
        self.assertIn('Pilot - Canaux - Modifier un canal', self.browser.title)

        self.browser.find_element_by_id('id_name').send_keys('New title 2')
        self.browser.find_element_by_tag_name('button').click()

        # Go to changelog page for this channel to check we have 2 entries
        url = reverse('ui_channel_history', kwargs={'channel_pk': channel.pk, })

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Since we have 2 versions, we should have 2 diff.
        url_api = reverse('activity_api_list')
        url_api_queryparam = '{0}?object_type={1}&object_id={2}&page=1'.format(url_api,
                                                                               channel_content_type.pk,
                                                                               channel.pk)
        response_api = json.loads(self.client.get(url_api_queryparam).content)
        self.assertEquals(2, response_api['count'])

    def test_channeltoken_view(self):
        """Test channel token detail view."""

        channel = channels_factories.ChannelFactory.create(desk=self.desk, type='cms')
        api_token = api_factories.ApiTokenFactory.create(desk=self.desk, channels=[channel])

        # Test GET.
        url = reverse('ui_channeltoken_detail', kwargs={'channeltoken_pk': api_token.pk, })
        response = self.client.get(url)

        self.assertContains(response, api_token.key)

    def test_channeltoken_in_channel_detail(self):
        """Test channel detail ."""
        channel = channels_factories.ChannelFactory.create(desk=self.desk, type='cms')
        api_factories.ApiTokenFactory.create(desk=self.desk, channels=[channel])

        # Test GET.
        response = self.client.get(reverse('ui_channel_detail', args=[channel.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Voir la clé')

    def test_channeltoken_create(self):
        """Test channel add."""

        channel = channels_factories.ChannelFactory.create(desk=self.desk, type='cms')

        # Test GET.
        url = reverse('ui_channeltoken_add', kwargs={'channel_pk': channel.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.channels_list_url)

        # Check created Channel token.
        # self.assertTrue(channel.channeltoken)
        # This view now create an APIToken
        self.assertTrue(channel.api_tokens.exists())
        api_token = channel.api_tokens.all()[0]

        # The just added Channel Token view link must appears in the channels list.
        response = self.client.get(reverse('ui_channel_detail', args=[channel.pk]))

        detail_url = reverse('ui_channeltoken_detail', kwargs={'channeltoken_pk': api_token.pk})
        self.assertContains(response, detail_url, count=1)

    def test_channeltoken_delete(self):
        """Test channel token delete."""
        channel = channels_factories.ChannelFactory.create(desk=self.desk, type='cms')
        api_token = api_factories.ApiTokenFactory.create(desk=self.desk, channels=[channel])
        url = reverse('ui_channeltoken_delete', kwargs={'channeltoken_pk': api_token.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        response = self.client.post(url, data={'action': 'delete', })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.channels_list_url)

        # The Channel token should have been deleted.
        self.assertEqual(ChannelToken.objects.count(), 0)

    @skip("Social features disabled for now")
    def test_twitter_credentials(self):
        """Test twitter credentials view."""

        twitter_credentials = channels_factories.TwitterCredentialFactory.create(channel__desk=self.desk)
        url = reverse('ui_twitter_credentials_detail', kwargs={'credentials_pk': twitter_credentials.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gestion de la connection au compte Twitter")

    @patch('tweepy.API.verify_credentials', fake_api)
    def test_twitter_credentials_token_validity(self):
        twitter_credentials = channels_factories.TwitterCredentialFactory.create(channel__desk=self.desk)

        url = reverse('ui_twitter_check_token_valid', kwargs={'credentials_pk': twitter_credentials.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @skip("Social features disabled for now")
    def test_facebook_credentials(self):
        """Test facebook credentials view."""

        facebook_credentials = channels_factories.FacebookCredentialFactory.create(channel__desk=self.desk)
        url = reverse('ui_facebook_credentials_detail', kwargs={'credentials_pk': facebook_credentials.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gestion de la connexion au compte Facebook")

    @patch('pilot.channels.models.FacebookCredential.check_validity', fake_api)
    @patch('pilot.channels.models.FacebookCredential.check_publish_permissions', fake_api)
    def test_facebook_credentials_token_validity(self):
        facebook_credentials = channels_factories.FacebookCredentialFactory.create(channel__desk=self.desk)

        url = reverse('ui_facebook_check_token_valid', kwargs={'credentials_pk': facebook_credentials.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class ChannelsUiEditorTest(PilotEditorUserMixin, TestCase):
    def test_channels_list(self):
        """Test channels list."""

        # Test GET.
        response = self.client.get(reverse('ui_channels_list'))
        self.assertEqual(response.status_code, 200)
        # Css class whose purpose is to test the add channel button presence
        # Editors can't add channels so they don't need this button
        self.assertNotContains(response, "tst__channel-add")

    def test_channels_detail(self):
        """Test channel detail page."""

        channel = channels_factories.ChannelFactory.create(desk=self.desk)

        # Test GET.
        response = self.client.get(reverse('ui_channel_detail', args=[channel.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, channel.name)

        # Editors can't neither edit channels nor delete them so they don't need theses buttons
        self.assertNotContains(response, "tst__channel-delete")
        self.assertNotContains(response, "tst__channel-edit")


class ChannelsUiRestrictedEditorTest(PilotRestrictedEditorUserMixin, TestCase):
    def test_channels_list(self):
        """Test channels list."""

        # Test GET.
        response = self.client.get(reverse('ui_channels_list'))
        self.assertEqual(response.status_code, 200)
        # Css class whose purpose is to test the add channel button presence
        # Restricted editors can't add channels so they don't need this button
        self.assertNotContains(response, "tst__channel-add")

    def test_channels_detail(self):
        """Test channel detail page."""
        channel = channels_factories.ChannelFactory.create(desk=self.desk)

        # Test GET.
        response = self.client.get(reverse('ui_channel_detail', args=[channel.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, channel.name)

        # Restricted editors can't neither edit channels nor delete them so they don't need theses buttons
        self.assertNotContains(response, "tst__channel-delete")
        self.assertNotContains(response, "tst__channel-edit")

    @skip("View obsoleted by the new Vue.js UI")
    def test_channel_add(self):
        """Test channel add."""

        url = reverse('ui_channel_add')

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Test POST.

        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 403)

    def test_channel_edit(self):
        """Test channel edit."""

        channel = channels_factories.ChannelFactory.create(desk=self.desk)
        url = reverse('ui_channel_edit', kwargs={'channel_pk': channel.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Test POST.
        response = self.client.post(url, data={})
        self.assertEqual(response.status_code, 403)

    def test_channel_close(self):
        """Test channel close."""

        channel = channels_factories.ChannelFactory.create(desk=self.desk)
        url = reverse('ui_channel_close_or_delete', kwargs={'channel_pk': channel.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Test POST.
        response = self.client.post(url, data={'action': 'close', })
        self.assertEqual(response.status_code, 403)

    def test_channel_delete(self):
        """Test channel delete."""

        channel = channels_factories.ChannelFactory.create(desk=self.desk)
        url = reverse('ui_channel_close_or_delete', kwargs={'channel_pk': channel.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Test POST.
        response = self.client.post(url, data={'action': 'delete', })
        self.assertEqual(response.status_code, 403)

        # TODO : replace all this by a proper API test
#    def test_channels_list_data(self):
#         """Test channels list data for restricted editors."""
#         Channel.objects.all().delete()
#         channels_factories.ChannelFactory.reset_sequence(1)  # we reset explictly factories sequences to ease testing
#         channels_factories.ChannelFactory.create_batch(size=5, desk=self.desk)
#         owner = user_factories.RestrictedEditorFactory.create()
#         other_owner = user_factories.RestrictedEditorFactory.create()
#         owner.organisation = self.desk.organization
#         owner.save()
#
#         channels = Channel.objects.order_by('-created_at')
#
#         # Test GET. Users is a restricted and does not own any channel, so he does not see any of them
#         url = '/channels/list-data/?length=30&' + '&'.join(['columns[{0}][search][value]='.format(i) for i in range(4)])
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.content)
#         self.assertEqual(data['result'], 'ok')
#         self.assertEqual(data['recordsTotal'], 0)
#         self.assertEqual(data['recordsFiltered'], 0)
#         self.assertEqual(len(data['data']), 0)
#
#         # Test GET. No user own 2 channels, one alone and one he shares with another user, so he must see 2 channels
#         channels[0].owners.add(self.restricted_user)
#         channels[1].owners.add(self.restricted_user, other_owner)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         data = json.loads(response.content)
#         print(data)
#         self.assertEqual(data['result'], 'ok')
#         self.assertEqual(data['recordsTotal'], 2)
#         self.assertEqual(data['recordsFiltered'], 2)
#         self.assertEqual(len(data['data']), 2)
#
#         for i in range(0, 1):
#             self.assertTrue(channels[i].name in data['data'][i][0])
#             self.assertTrue(channels[i].get_absolute_url() in data['data'][i][0])
#             self.assertTrue(channels[i].type in data['data'][i][1])
#             self.assertTrue(channels[i].description in data['data'][i][2])
#             self.assertTrue(unicode(channels[i].state) in data['data'][i][3])
