import datetime
import os
from unittest.case import skip

import pytz
from django.core import mail
from django.urls import reverse
from django.test import TestCase, override_settings

from django.utils import timezone
from django.conf import settings

from pilot.activity_stream.models import Activity
from pilot.assets.tests import factories as assets_factories
from pilot.projects.tests import factories as projects_factories
from pilot.channels.tests import factories as channels_factories
from pilot.pilot_users.tests import factories as user_factories
from pilot.targets.tests import factories as targets_factories
from pilot.utils.test import PilotAdminUserMixin, PilotRestrictedEditorUserMixin, MediaMixin


@override_settings(MEDIA_ROOT=MediaMixin.TEST_MEDIA_ROOT)
class projectsUiTest(MediaMixin, PilotAdminUserMixin, TestCase):
    def setUp(self):
        super(projectsUiTest, self).setUp()
        # Keep a reference to the list view URL.
        self.projects_list_url = reverse('ui_projects_list')

    def tearDown(self):
        super(projectsUiTest, self).tearDown()
        # Delete all Project objects after each test.
        Project.objects.all().delete()

    def test_projects_list(self):
        """Test projects list."""

        # Test GET.
        response = self.client.get(self.projects_list_url)
        self.assertEqual(response.status_code, 200)

    # TODO : replace all this by a proper API test
    # def test_projects_list_data(self):
    #     """Test json data for the the main list view."""
    #     projects_factories.ProjectFactory.create_batch(size=10, desk=self.desk)
    #     tz = timezone.utc
    #     # Wait a milisecond to ensure different creation time
    #     time.sleep(0.001)
    #     project = projects_factories.ProjectFactory.create(name=u"Namé", desk=self.desk,
    #                                                           start=datetime.datetime(2054, 7, 1, tzinfo=tz),
    #                                                           end=datetime.datetime(2054, 7, 31, tzinfo=tz))
    #     projects_factories.ProjectFactory.create_batch(size=3)  # other desk projects
    #
    #     # Test json data.
    #     url = '/project/list-data/?length=30&' + '&'.join(['columns[{}][search][value]='.format(i) for i in range(9)])
    #     response = self.client.get(url)
    #     data = json.loads(response.content)
    #     self.assertEqual(data['result'], 'ok')
    #     self.assertEqual(data['recordsTotal'], 11)
    #     self.assertEqual(data['recordsFiltered'], 11)
    #     self.assertEqual(len(data['data']), 11)
    #     self.assertTrue(u"Namé" in data['data'][0][1])
    #
    #     # Paginating the results
    #     response = self.client.get(url + '&length=5')
    #     data = json.loads(response.content)
    #     self.assertEqual(data['result'], 'ok')
    #     self.assertEqual(len(data['data']), 5)
    #
    #     # test filter on id
    #     response = self.client.get(
    #         url.replace('columns[0][search][value]=', 'columns[0][search][value]={}'.format(project.id)))
    #     data = json.loads(response.content)
    #     self.assertEqual(data['recordsFiltered'], 1)
    #     self.assertEqual(str(project.id), data['data'][0][0])
    #
    #     # test filter on name
    #     response = self.client.get(url.replace('columns[1][search][value]=', 'columns[1][search][value]=namè'))
    #     data = json.loads(response.content)
    #     self.assertEqual(data['recordsFiltered'], 1)
    #     self.assertTrue(u"Namé" in data['data'][0][1])
    #
    #     # test filter on start
    #     response = self.client.get(url.replace('columns[2][search][value]=', 'columns[2][search][value]=31/07/2054'))
    #     data = json.loads(response.content)
    #     self.assertEqual(data['recordsFiltered'], 1)
    #     response = self.client.get(url.replace('columns[2][search][value]=', 'columns[2][search][value]=01/08/2054'))
    #     data = json.loads(response.content)
    #     self.assertEqual(data['recordsFiltered'], 0)
    #
    #     # test filter on end
    #     response = self.client.get(url.replace('columns[3][search][value]=', 'columns[3][search][value]=30/06/2054'))
    #     data = json.loads(response.content)
    #     self.assertEqual(data['recordsFiltered'], 10)
    #     response = self.client.get(url.replace('columns[3][search][value]=', 'columns[3][search][value]=01/07/2054'))
    #     data = json.loads(response.content)
    #     self.assertEqual(data['recordsFiltered'], 11)
    #
    #     # testing the name row in datatable
    #     request = RequestFactory().get(url)
    #     view = ProjectListView()
    #     view.request = request
    #
    #     # Non outdated project
    #     row = projects_factories.ProjectFactory(
    #         desk=self.desk,
    #         start=timezone.now(),
    #         end=timezone.now() + datetime.timedelta(days=10)
    #     )
    #     self.assertFalse(u'Terminé' in view._render_name(row))
    #
    #     # Outdated project
    #     row = projects_factories.ProjectFactory(
    #         desk=self.desk,
    #         start=timezone.now() - datetime.timedelta(days=15),
    #         end=timezone.now() - datetime.timedelta(days=10)
    #     )
    #     self.assertTrue(u'Terminé' in view._render_name(row))

    def test_projectform(self):
        # Testing ProjectForm, iot be sure it does not display external targets
        targets_factories.TargetFactory()  # targets related to an other desk
        form = ProjectForm(desk=self.desk)
        self.assertEqual(form.fields.get('targets'), None)
        expected_fields = set([u'color', u'label', u'description', u'end', u'name', u'notify_channel_owner', u'owners', u'priority', u'start'])
        self.assertEqual(expected_fields, set(form.fields.keys()))

    @skip("View obsoleted by the new Vue.js UI")
    def test_project_add_without_owners(self):
        """Test project add without owners."""

        url = reverse('ui_project_add')

        start = (timezone.now().date() + datetime.timedelta(days=10))
        end = start + datetime.timedelta(days=10)

        channel = channels_factories.ChannelFactory.create(desk=self.desk)

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        open(os.path.join(settings.MEDIA_ROOT, "test.png"), "wb").close()
        # Test POST.
        post_data = {
            'name': 'Project name',
            'start': start.strftime('%Y-%m-%d'),
            'end': end.strftime('%Y-%m-%d'),
            'channels': [channel.pk],
            'description': 'Project description',
            'notify_channel_owner': True,
            'priority': '3_normal',
        }

        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.projects_list_url)

        # Check added Project.
        project = Project.objects.get(name=post_data['name'])
        self.assertEqual(project.desk, self.desk)
        self.assertEqual(project.owners.count(), 0)
        self.assertEqual(project.state, states.STATE_ACTIVE)
        self.assertIn(channel, project.channels.all())
        self.assertEqual(start, project.start)
        self.assertEqual(end, project.end)

    @skip("View obsoleted by the new Vue.js UI")
    def test_project_add_with_owners(self):
        """Test project add with owners."""

        url = reverse('ui_project_add')

        start = (timezone.now().date() + datetime.timedelta(days=10))
        end = start + datetime.timedelta(days=10)
        owners = user_factories.PilotUserFactory.create_batch(2)
        self.desk.users.add(*owners)
        channel = channels_factories.ChannelFactory.create(desk=self.desk)

        open(os.path.join(settings.MEDIA_ROOT, "test.png"), "wb").close()
        # Test POST.
        post_data = {
            'name': 'Project name',
            'start': start.strftime('%Y-%m-%d'),
            'end': end.strftime('%Y-%m-%d'),
            'channels': [channel.pk],
            'owners': [o.pk for o in owners],
            'description': 'Project description',
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '',
            'form-MAX_NUM_FORMS': '',
            'form-0-file': 'test.png',
            'form-0-title': 'asset title',
            'notify_channel_owner': True,
            'priority': '3_normal',
        }

        self.client.post(url, data=post_data)

        # Check added Project.
        project = Project.objects.get(name=post_data['name'])
        self.assertEqual(project.desk, self.desk)
        self.assertEqual(project.owners.count(), 2)

    @skip("View obsoleted by the new Vue.js UI")
    def test_user_email_notification_on_project_add(self):
        """Test project add."""

        url = reverse('ui_project_add')

        start = (timezone.now().date() + datetime.timedelta(days=10))
        end = start + datetime.timedelta(days=10)

        channel = channels_factories.ChannelFactory.create(desk=self.desk)
        owners = user_factories.PilotUserFactory.create_batch(3)
        channel.owners.add(*owners)
        channel_without_owner = channels_factories.ChannelFactory.create(desk=self.desk)

        open(os.path.join(settings.MEDIA_ROOT, "test.png"), "wb").close()
        open(os.path.join(settings.MEDIA_ROOT, "test2.png"), "wb").close()
        open(os.path.join(settings.MEDIA_ROOT, "test3.png"), "wb").close()
        # Test POST.
        post_data = {
            'name': 'Project name',
            'start': start.strftime('%Y-%m-%d'),
            'end': end.strftime('%Y-%m-%d'),
            'channels': [channel.pk],
            'description': 'Project description',
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '',
            'form-MAX_NUM_FORMS': '',
            'form-0-file': 'test.png',
            'form-0-title': 'asset title',
            'priority': '3_normal',
        }
        # Channel has no owner so no email is sent
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        post_data['notify_channel_owner'] = True
        self.assertEqual(len(mail.outbox), 0)

        # One channel has owners but notify field is set to false so no email is sent
        post_data['channels'] = [channel_without_owner.pk, channel.pk]
        post_data['notify_channel_owner'] = False
        post_data['form-0-file'] = 'test2.png',

        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

        # One channel has owners and notify field is set to true so one email is sent
        post_data['form-0-file'] = 'test3.png'
        post_data['notify_channel_owner'] = True
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)

        # Check we have our 3 owners in the recipients and no more
        self.assertEqual(len(mail.outbox[0].to), 3)
        for o in owners:
            self.assertTrue(o.email in mail.outbox[0].to)
        self.assertEqual(
            mail.outbox[0].subject,
            "Notification : Une projet sollicitant votre canal a été mise à jour"
        )

    def test_active_project_detail(self):
        owner = user_factories.PilotUserFactory()
        active_project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
            created_by_external_email='external.email@pilot.pm'
        )
        active_project.owners.add(owner)
        url = reverse('ui_project_detail', kwargs={'project_pk': active_project.pk})
        response = self.client.get(url)
        self.assertContains(response, active_project.name)
        self.assertContains(response, active_project.created_by_external_email)
        self.assertContains(response, active_project.owners.all()[0].username)

    def test_created_by_external_project_detail(self):
        project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
            created_by_external_email='external@something.com'
        )

        url = reverse('ui_project_detail', kwargs={'project_pk': project.pk})
        response = self.client.get(url)
        self.assertContains(response, project.created_by_external_email)

    @skip("This has been vueified, test should be rewritten")
    def test_closed_project_detail(self):
        closed_project = projects_factories.ProjectFactory.create(
            desk=self.desk, state=states.STATE_CLOSED)

        url = reverse('ui_project_detail', kwargs={'project_pk': closed_project.pk})
        response = self.client.get(url)
        self.assertNotContains(response, "Nouveau contenu pour ce projet")
        self.assertContains(response, "Réouvrir")

    def test_project_edit(self):
        """Test project edit."""

        # Create an `active` project.
        project = projects_factories.ProjectFactory.create(
            desk=self.desk, state=states.STATE_ACTIVE)
        asset = assets_factories.AssetFactory(desk=self.desk)
        project.assets.add(asset)

        channels = channels_factories.ChannelFactory.create_batch(size=2, desk=self.desk)

        # To trigger the mail notification channel must have an owner
        user_factories.PilotUserFactory()  # owner
        channels[0].owners.add()

        url = reverse('ui_project_edit', kwargs={'project_pk': project.pk})
        start = (timezone.now().date() + datetime.timedelta(days=10))
        end = start + datetime.timedelta(days=10)

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        open(os.path.join(settings.MEDIA_ROOT, "test.png"), "wb").close()
        # Test POST.
        post_data = {
            'name': u'New Project namé',
            'owners': [self.user.pk],
            'start': start.strftime('%Y-%m-%d'),
            'end': end.strftime('%Y-%m-%d'),
            'channels': [c.pk for c in channels],
            'description': u'New Project descrîption',
            'priority': '3_normal',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_project_detail', kwargs={'project_pk': project.pk}))

        # Check edited Item.
        project = Project.objects.get(pk=project.pk)
        self.assertEqual(project.desk, self.desk)
        self.assertEqual(project.owners.count(), 1)
        self.assertEqual(project.owners.all()[0].pk, self.user.pk)
        self.assertEqual(project.name, post_data['name'])
        self.assertEqual(project.updated_by, self.user)
        for channel in channels:
            self.assertIn(channel, project.channels.all())
        self.assertEqual(project.description, post_data['description'])
        self.assertEqual(start, project.start)
        self.assertEqual(end, project.end)

    def test_project_edit_without_channel(self):
        """Test project edit."""

        # Create an `active` project.
        project = projects_factories.ProjectFactory.create(
            desk=self.desk, state=states.STATE_ACTIVE)
        asset = assets_factories.AssetFactory(desk=self.desk)
        project.assets.add(asset)

        # To trigger the mail notification channel must have an owner
        owner = user_factories.PilotUserFactory()

        url = reverse('ui_project_edit', kwargs={'project_pk': project.pk})
        start = (timezone.now().date() + datetime.timedelta(days=10))
        end = start + datetime.timedelta(days=10)

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        open(os.path.join(settings.MEDIA_ROOT, "test.png"), "wb").close()

        # Test POST.
        post_data = {
            'name': u'New Project namé',
            'owners': [self.user.pk],
            'start': start.strftime('%Y-%m-%d'),
            'end': end.strftime('%Y-%m-%d'),
            'description': u'New Project descrîption',
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '',
            'form-MAX_NUM_FORMS': '',
            'notify_channel_owner': True,
            'form-0-file': "test.png",
            'form-0-title': 'new asset title',
            'priority': '3_normal',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_project_detail', kwargs={'project_pk': project.pk}))

    def test_project_remove_channel(self):
        """Check removing a channel works fine."""

        # Create an `active` project.
        project = projects_factories.ProjectFactory.create(
            desk=self.desk, state=states.STATE_ACTIVE)

        channels = channels_factories.ChannelFactory.create_batch(size=2, desk=self.desk)

        # To trigger the mail notification channel must have an owner
        channels[0].owners.add(*user_factories.PilotUserFactory.create_batch(3))
        channels[1].owners.add(*user_factories.PilotUserFactory.create_batch(2))

        project.channels.add(*channels)
        url = reverse('ui_project_edit', kwargs={'project_pk': project.pk})
        start = (timezone.now().date() + datetime.timedelta(days=10))
        end = start + datetime.timedelta(days=10)

        # Test POST.

        post_data = {
            'name': u'New Project namé',
            'owner': self.user.pk,
            'start': start.strftime('%Y-%m-%d'),
            'end': end.strftime('%Y-%m-%d'),
            'channels': [channels[0].pk],  # 1 pk instead of 2.
            'description': u'New Project descrîption',
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 10,
            'priority': '3_normal',
        }
        self.client.post(url, data=post_data)

        # Check edited Item.
        project = Project.objects.get(pk=project.pk)
        self.assertEqual(project.channels.count(), 1)  # Only 1 channel left
        self.assertEqual(project.channels.all()[0].pk, channels[0].pk)

    def test_user_notification_on_project_edit(self):
        """Test if channel user are notified on project edit."""

        # Create an `active` project.
        project = projects_factories.ProjectFactory.create(
            desk=self.desk, state=states.STATE_ACTIVE)
        asset = assets_factories.AssetFactory(desk=self.desk)
        project.assets.add(asset)

        channels = channels_factories.ChannelFactory.create_batch(size=3, desk=self.desk)
        # To trigger the mail notification channel must have an owner
        owners_c1 = user_factories.PilotUserFactory.create_batch(3)
        owners_c2 = user_factories.PilotUserFactory.create_batch(2)
        channels[0].owners.add(*owners_c1)
        channels[0].owners.add(*owners_c2)

        url = reverse('ui_project_edit', kwargs={'project_pk': project.pk})
        start = (timezone.now().date() + datetime.timedelta(days=10))
        end = start + datetime.timedelta(days=10)
        # Test POST.
        post_data = {
            'name': u'New Project namé',
            'owner': self.user.pk,
            'start': start.strftime('%Y-%m-%d'),
            'end': end.strftime('%Y-%m-%d'),
            'channels': [c.pk for c in channels],
            'description': u'New Project descrîption',
            'notify_channel_owner': False,
            'form-TOTAL_FORMS': ['2'],
            'form-INITIAL_FORMS': ['0'],
            'form-MIN_NUM_FORMS': '',
            'form-MAX_NUM_FORMS': '',
            'form-0-id': [''],
            'priority': '3_normal',
        }

        # No notification because notify field is false
        self.client.post(url, data=post_data)
        self.assertEqual(len(mail.outbox), 0)

        # Reset channels
        updated_project = Project.objects.all()[0]
        updated_project.channels.clear()

        # Notification when channel with owners are added
        post_data['notify_channel_owner'] = True
        self.client.post(url, data=post_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].to), 5)
        for o in owners_c1:
            self.assertTrue(o.email in mail.outbox[0].to)
        for o in owners_c2:
            self.assertTrue(o.email in mail.outbox[0].to)
        self.assertEqual(
            mail.outbox[0].subject,
            "Notification : Un projet sollicitant votre canal a été mis à jour"
        )

        # Reset mailbox
        mail.outbox = []
        # Reset channels
        updated_project = Project.objects.all()[0]
        updated_project.channels.clear()
        # No notification when a channel without owner is added
        post_data['channels'] = [channels[1].pk, channels[2].pk]
        self.client.post(url, data=post_data)
        self.assertEqual(len(mail.outbox), 0)

        # Reset mailbox
        mail.outbox = []
        # No notification when a channel without owner is removed

        updated_project = Project.objects.all()[0]
        url = reverse('ui_project_edit', kwargs={'project_pk': updated_project.pk})
        post_data['channels'] = [channels[0].pk]
        self.client.post(url, data=post_data)
        self.assertEqual(len(mail.outbox), 0)

        # Reset mailbox
        mail.outbox = []

        # Notification when a channel with owner is removed
        post_data['channels'] = [channels[2].pk]
        self.client.post(url, data=post_data)

        # Checking 1 message, 5 recipients
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].to), 5)
        for o in owners_c1:
            self.assertTrue(o.email in mail.outbox[0].to)
        for o in owners_c2:
            self.assertTrue(o.email in mail.outbox[0].to)
        self.assertEqual(
            mail.outbox[0].subject,
            "Notification : Un projet sollicitant votre canal a été mis à jour"
        )

    def test_project_edit_tags(self):
        """Test project tags edition."""

        # Create an `active` project.
        project = projects_factories.ProjectFactory.create(
            desk=self.desk, state=states.STATE_ACTIVE)

        url = reverse('ui_project_edit_tags', kwargs={'project_pk': project.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        post_data = {
            'tags': 'tag1, tag2',
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_project_detail', kwargs={'project_pk': project.pk}))

        # Check tags.
        self.assertEqual(2, project.tags.all().count())
        for tag in ['tag1', 'tag2']:
            self.assertEqual(1, project.tags.filter(name__exact=tag).count())

    def test_project_close(self):
        """Test project close."""

        start = (timezone.now().date() + datetime.timedelta(days=10))
        end = start + datetime.timedelta(days=10)

        # Create an `active` project.
        project = projects_factories.ProjectFactory.create(
            desk=self.desk, state=states.STATE_ACTIVE, start=start, end=end)

        url = reverse('ui_project_close_or_delete', kwargs={'project_pk': project.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        response = self.client.post(url, data={'action': 'close', })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_project_detail', kwargs={'project_pk': project.pk}))

        # The Project should have been closed but should remain in the projects list.
        # response = self.client.get(self.projects_list_url)
        project = Project.objects.get(pk=project.pk)
        # self.assertIn(project, response.context['projects'])
        self.assertEqual(project.state, states.STATE_CLOSED)
        self.assertEqual(project.updated_by, self.user)

        self.assertEqual(start, project.start)
        self.assertEqual(end, project.end)

    def test_project_reopen(self):
        """Test project reopen."""

        start = (timezone.now().date() + datetime.timedelta(days=10))
        end = start + datetime.timedelta(days=10)

        # Create a `closed` project.
        project = projects_factories.ProjectFactory.create(
            desk=self.desk, state=states.STATE_CLOSED, start=start, end=end)

        url = reverse('ui_project_reopen', kwargs={'project_pk': project.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        response = self.client.post(url, data={'action': 'reopen', })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_project_detail', kwargs={'project_pk': project.pk}))

        # The Project should have been reopened but.
        # response = self.client.get(self.projects_list_url)
        project = Project.objects.get(pk=project.pk)
        # self.assertIn(project, response.context['projects'])
        self.assertEqual(project.state, states.STATE_ACTIVE)
        self.assertEqual(project.updated_by, self.user)

        self.assertEqual(start, project.start)
        self.assertEqual(end, project.end)

        activity = Activity.objects.latest('created_at')
        self.assertEqual(activity.desk, self.desk)
        self.assertEqual(activity.target_object_id, project.pk)
        self.assertEqual(activity.verb, Activity.VERB_RESTORED)

    def test_project_delete(self):
        """Test project delete."""

        # Create an `active` project.
        project = projects_factories.ProjectFactory.create(
            desk=self.desk, state=states.STATE_ACTIVE)
        asset = assets_factories.AssetFactory(desk=self.desk, in_media_library=False)
        project.assets.add(asset)

        url = reverse('ui_project_close_or_delete', kwargs={'project_pk': project.pk})

        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test POST.
        response = self.client.post(url, data={'action': 'delete', })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.projects_list_url)

        # The Project should have been deleted.
        self.assertEqual(Project.objects.all().count(), 0)

        # The Asset should have been deleted.
        self.assertEqual(Asset.objects.count(), 0)

    # TODO : replace this by a a test on the project detail page
    # def test_project_history(self):
    #     """Test the history view of a project."""
    #
    #     project = projects_factories.ProjectFactory.create(
    #         desk=self.desk, state=states.STATE_ACTIVE)
    #     owners = user_factories.PilotUserFactory.create_batch(2)
    #     project.owners.add(owners[0])
    #
    #     # Create 2 versions.
    #     with reversion.create_revision():
    #         project.name = 'Name 1'
    #         project.save()
    #     with reversion.create_revision():
    #         project.name = 'Name 2'
    #         project.save()
    #         project.owners.add(owners[1])
    #     self.assertEqual(2, reversion_models.Version.objects.filter(object_id=project.pk).count())
    #
    #     url = reverse('ui_project_history', kwargs={'project_pk': project.pk, })
    #
    #     # Test GET.
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #
    #     # Since we have 2 versions, we should have 1 diff.
    #     self.assertEqual(2, len(reversion.get_for_object(project)))


class projectsUiRestrictedEditorPermsTest(PilotRestrictedEditorUserMixin, TestCase):
    """Test access perms for a `restricted editor` user."""

    @skip("ui_project_add has been replaved by an API call. What should we test here ?")
    def test_access_perms(self):
        projects_factories.ProjectFactory.create(desk=self.desk)

        # Should be able to view the project list.
        response = self.client.get(reverse('ui_projects_list'))
        self.assertEqual(response.status_code, 200)

        # Should *NOT* be able to add a project.
        response = self.client.get(reverse('ui_project_add'))
        self.assertEqual(response.status_code, 403)

    # TODO : replace all this by a proper API test
    # def test_projects_list(self):
    #     """A `restricted editor` should view only the project that he owns."""
    #
    #     project1 = projects_factories.ProjectFactory.create(desk=self.desk)
    #     project1.owners.add(self.user)
    #     project2 = projects_factories.ProjectFactory.create(desk=self.desk)
    #     project2.owners.add(self.restricted_user)
    #
    #     # Test GET.
    #     url = '/project/list-data/?' + '&'.join(['columns[{}][search][value]='.format(i) for i in range(9)])
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.content)
    #
    #     self.assertEqual(1, data['recordsTotal'])
    #     self.assertEqual(1, data['recordsFiltered'])
    #     self.assertEqual(1, len(data['data']))
    #     self.assertEqual(str(project2.pk), data['data'][0][0])
    #
    #     project2.delete()
    #
    #     # Creating a project `created_by` a restricted_user
    #     project3 = projects_factories.ProjectFactory.create(desk=self.desk, created_by=self.restricted_user)
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.content)
    #
    #     self.assertEqual(1, data['recordsTotal'])
    #     self.assertEqual(1, data['recordsFiltered'])
    #     self.assertEqual(1, len(data['data']))
    #     self.assertEqual(str(project3.pk), data['data'][0][0])

    def test_active_project_detail(self):
        # Project owned by somebody else
        owner = user_factories.PilotUserFactory()
        owned_by_sb_else_project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
        )
        owned_by_sb_else_project.owners.add(owner)
        url = reverse('ui_project_detail', kwargs={'project_pk': owned_by_sb_else_project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # Project created by somebody else
        created__by_sb_else_project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
        )
        url = reverse('ui_project_detail', kwargs={'project_pk': created__by_sb_else_project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # Project created by restricted editor
        created__by_restricted_editor__project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
            created_by=self.restricted_user,
        )
        url = reverse('ui_project_detail', kwargs={'project_pk': created__by_restricted_editor__project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, created__by_restricted_editor__project.name)
        self.assertContains(response, self.restricted_user.username)

        # Project owned by restricted editor
        owned__by_restricted_editor__project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
        )
        owned__by_restricted_editor__project.owners.add(self.restricted_user)
        url = reverse('ui_project_detail', kwargs={'project_pk': owned__by_restricted_editor__project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, owned__by_restricted_editor__project.name)
        self.assertContains(response, self.restricted_user.username)

    def test_active_project_edit(self):
        # Project owned by somebody else
        owner = user_factories.PilotUserFactory()
        owned_by_sb_else_project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
        )
        owned_by_sb_else_project.owners.add(owner)
        url = reverse('ui_project_edit', kwargs={'project_pk': owned_by_sb_else_project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # Project created by somebody else
        created__by_sb_else_project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
        )
        url = reverse('ui_project_edit', kwargs={'project_pk': created__by_sb_else_project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # Project created by restricted editor
        created__by_restricted_editor__project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
            created_by=self.restricted_user,
        )
        url = reverse('ui_project_edit', kwargs={'project_pk': created__by_restricted_editor__project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, created__by_restricted_editor__project.name)
        self.assertContains(response, self.restricted_user.username)

        # Project owned by restricted editor
        owned__by_restricted_editor__project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
        )
        owned__by_restricted_editor__project.owners.add(self.restricted_user)
        url = reverse('ui_project_edit', kwargs={'project_pk': owned__by_restricted_editor__project.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, owned__by_restricted_editor__project.name)
        self.assertContains(response, self.restricted_user.username)

    def test_active_project_edit_tags(self):
        # Project owned by somebody else
        owner = user_factories.PilotUserFactory()
        owned_by_sb_else_project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
        )
        owned_by_sb_else_project.owners.add(owner)

        post_data = {
            'tags': 'tag1, tag2',
        }

        url = reverse('ui_project_edit_tags', kwargs={'project_pk': owned_by_sb_else_project.pk})
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 404)

        # Project created by somebody else
        created__by_sb_else_project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
        )
        url = reverse('ui_project_edit_tags', kwargs={'project_pk': created__by_sb_else_project.pk})
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 404)

        # Project created by restricted editor
        created__by_restricted_editor__project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
            created_by=self.restricted_user,
        )
        url = reverse('ui_project_edit_tags', kwargs={'project_pk': created__by_restricted_editor__project.pk})
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        # Check tags.
        self.assertEqual(2, created__by_restricted_editor__project.tags.all().count())
        for tag in ['tag1', 'tag2']:
            self.assertEqual(1, created__by_restricted_editor__project.tags.filter(name__exact=tag).count())

        # Project owned by restricted editor
        owned__by_restricted_editor__project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
        )
        owned__by_restricted_editor__project.owners.add(self.restricted_user)
        url = reverse('ui_project_edit_tags', kwargs={'project_pk': owned__by_restricted_editor__project.pk})
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('ui_project_detail', kwargs={'project_pk': owned__by_restricted_editor__project.pk})
        )
        # Check tags.
        self.assertEqual(2, owned__by_restricted_editor__project.tags.all().count())
        for tag in ['tag1', 'tag2']:
            self.assertEqual(1, owned__by_restricted_editor__project.tags.filter(name__exact=tag).count())

    def test_active_project_delete(self):
        # Project owned by somebody else
        owner = user_factories.PilotUserFactory()
        owned_by_sb_else_project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
        )
        owned_by_sb_else_project.owners.add(owner)

        post_data = {'action': 'delete', }

        url = reverse('ui_project_close_or_delete', kwargs={'project_pk': owned_by_sb_else_project.pk})
        # Get
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        # Post
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 404)

        # Project created by somebody else. Can't delete
        created__by_sb_else_project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
        )
        url = reverse('ui_project_close_or_delete', kwargs={'project_pk': created__by_sb_else_project.pk})

        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 404)

        # Project created by restricted editor. Can delete
        created__by_restricted_editor__project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
            created_by=self.restricted_user,
        )
        url = reverse('ui_project_close_or_delete',
                      kwargs={'project_pk': created__by_restricted_editor__project.pk})
        # Get
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Post
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_projects_list'))
        # The Project should have been deleted.
        self.assertEqual(
            Project.objects.filter(pk=created__by_restricted_editor__project.pk).count(),
            0)

        # Project owned by restricted editor. Can delete
        owned__by_restricted_editor__project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_ACTIVE,
        )
        owned__by_restricted_editor__project.owners.add(self.restricted_user)
        url = reverse('ui_project_close_or_delete', kwargs={'project_pk': owned__by_restricted_editor__project.pk})
        # Get
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Post
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ui_projects_list'))
        # The Project should have been deleted.
        self.assertEqual(
            Project.objects.filter(pk=owned__by_restricted_editor__project.pk).count(),
            0)

    def test_project_reopen(self):
        """Test project reopen."""

        start = (timezone.now().date() + datetime.timedelta(days=10))
        end = start + datetime.timedelta(days=10)

        # Project created by somebody else. Can't reopen.
        created_by_sb_else_project = projects_factories.ProjectFactory.create(
            desk=self.desk, state=states.STATE_CLOSED, start=start, end=end)

        url = reverse('ui_project_reopen', kwargs={'project_pk': created_by_sb_else_project.pk})
        post_data = {'action': 'reopen', }
        # Test GET.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # Test POST.
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 404)

        # Project owned by somebody else. Can't reopen.
        owner = user_factories.PilotUserFactory()
        owned_by_sb_else_project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_CLOSED,
            start=start,
            end=end
        )
        owned_by_sb_else_project.owners.add(owner)
        url = reverse('ui_project_reopen', kwargs={'project_pk': owned_by_sb_else_project.pk})

        # Get
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        # Post
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 404)
        owned_by_sb_else_project.delete()

        # Project created by user. Can reopen.
        created_by_restricted_user_project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_CLOSED,
            start=start,
            end=end,
            created_by=self.restricted_user
        )

        # Project owned by user. Can reopen.
        owned_by_restricted_user_project = projects_factories.ProjectFactory.create(
            desk=self.desk,
            state=states.STATE_CLOSED,
            start=start,
            end=end,
        )
        owned_by_restricted_user_project.owners.add(self.restricted_user)

        for camp in (created_by_restricted_user_project,):
            url = reverse('ui_project_reopen', kwargs={'project_pk': camp.pk})

            # Get
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            # Post
            response = self.client.post(url, data=post_data)
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(
                response,
                reverse('ui_project_detail', kwargs={'project_pk': camp.pk}))

            # The Project should have been reopened .
            project = Project.objects.get(pk=camp.pk)
            self.assertEqual(project.state, states.STATE_ACTIVE)
            self.assertEqual(project.updated_by, self.restricted_user)

            self.assertEqual(start, project.start)
            self.assertEqual(end, project.end)

            activity = Activity.objects.latest('created_at')
            self.assertEqual(activity.desk, self.desk)
            self.assertEqual(activity.target_object_id, project.pk)
            self.assertEqual(activity.verb, Activity.VERB_RESTORED)

    # TODO : replace this by a a test on the project detail page
    # def test_project_history(self):
    #     """Test the history view of a project."""
    #
    #     project = projects_factories.ProjectFactory.create(
    #         desk=self.desk, state=states.STATE_ACTIVE)
    #     owners = user_factories.PilotUserFactory.create_batch(2)
    #     project.owners.add(owners[0])
    #
    #     # Create 2 versions.
    #     with reversion.create_revision():
    #         project.name = 'Name 1'
    #         project.save()
    #     with reversion.create_revision():
    #         project.name = 'Name 2'
    #         project.save()
    #         project.owners.add(owners[1])
    #     self.assertEqual(2, reversion_models.Version.objects.filter(object_id=project.pk).count())
    #
    #     url = reverse('ui_project_history', kwargs={'project_pk': project.pk, })
    #     # User is neither owner nor creator. Can't access
    #     # Test GET.
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 404)
    #
    #     # User is owner. Can access
    #     camp = Project.objects.get(pk=project.pk)  # Need to get the model instance
    #     camp.owners.add(self.restricted_user)
    #     # Test GET.
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     # Since we have 2 versions, we should have 2 reversions.
    #     self.assertEqual(2, len(reversion.get_for_object(project)))
    #
    #     # User is creator. Can access
    #     camp.owners.remove(self.restricted_user)
    #     camp.created_by = self.restricted_user
    #     camp.save()
    #     # Test GET.
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     # Since we have 2 versions, we should have 2 reversions.
    #     self.assertEqual(2, len(reversion.get_for_object(project)))
