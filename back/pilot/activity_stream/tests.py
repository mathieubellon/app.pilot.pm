from unittest import skip

import mock

from django.urls import reverse
from django.test import TestCase

from pilot.activity_stream import factories as activity_stream_factories
from pilot.activity_stream.jobs import create_activity
from pilot.activity_stream.models import Activity
from pilot.items.tests import factories as items_factories
from pilot.utils.test import PilotAdminUserMixin
from pilot.desks.tests import factories as desks_factories


class FactoriesTests(TestCase):
    """Test Activity Factories."""

    def test_activity_factory(self):
        """Test ActivityFactory."""
        activity = activity_stream_factories.ActivityFactory.create()

        self.assertIsNotNone(activity.desk)
        self.assertIsNotNone(activity.actor)
        self.assertIsNotNone(activity.action_object)

        self.assertIsNone(activity.target)

        self.assertEqual('', activity.actor_email)
        self.assertEqual(activity.get_action_object_display(), activity.action_object_str)

        self.assertNotEqual('', activity.verb)

        self.assertEqual(activity.desk, activity.action_object.desk)


class ActivitySignalsTests(PilotAdminUserMixin, TestCase):
    """Test Activity Signals."""

    @mock.patch('logging.Logger.error')
    def test_invalid_actor(self, mock_logger):
        """
        Use an invalid `actor` value.

        This should not raise any Exception because activity creation is robust,
        but the Activity should not be created.
        """
        item = items_factories.ConfirmedItemFactory.create(desk=self.desk)
        create_activity(
            actor='toto',
            desk=self.desk,
            target=item,
            verb=Activity.VERB_CREATED
        )

        mock_logger.assert_called_once_with('Error while trying to send activity stream', exc_info=True)
        self.assertEqual(0, Activity.objects.all().count())

    def test_simple_verb(self):
        """Actor (PilotUser instance) and verb."""
        item = items_factories.ConfirmedItemFactory.create(desk=self.desk)
        create_activity(
            actor=self.user,
            desk=self.desk,
            target=item,
            verb=Activity.VERB_CREATED
        )

        # Test `activities_for`.
        self.assertEqual(1, Activity.activities_for(item, desk=self.desk).count())

        activity = self.desk.activity_stream.all()[0]
        self.assertEqual(activity.desk, self.desk)
        self.assertEqual(activity.actor, self.user)
        self.assertEqual(activity.verb, Activity.VERB_CREATED)
        self.assertEqual(activity.actor_email, '')
        self.assertIsNone(activity.action_object)
        self.assertEqual(activity.action_object_str, '')
        self.assertEqual(activity.target, item)

    def test_no_actor_object(self):
        """Actor (an email representing an anonymous/external user) and verb."""
        item = items_factories.ConfirmedItemFactory.create(desk=self.desk)
        create_activity(
            actor='momo@momo.com',
            desk=self.desk,
            target=item,
            verb=Activity.VERB_CREATED
        )
        activity = self.desk.activity_stream.get(actor_email='momo@momo.com')
        self.assertEqual(activity.desk, self.desk)
        self.assertIsNone(activity.actor)
        self.assertEqual(activity.actor_email, 'momo@momo.com')
        self.assertEqual(activity.verb, Activity.VERB_CREATED)
        self.assertIsNone(activity.action_object)
        self.assertEqual(activity.action_object_str, '')
        self.assertEqual(activity.target, item)

    def test_target(self):
        """Actor, verb and action object."""
        item = items_factories.ConfirmedItemFactory.create(desk=self.desk)
        create_activity(
            actor=self.user,
            desk=self.desk,
            verb=Activity.VERB_CREATED,
            target=item
        )

        # Test `activities_for`.
        self.assertEqual(1, Activity.activities_for(item, desk=self.desk).count())

        # Test reverse generic relationship.
        # Mute this one for the moment, don't understand it
        # self.assertEqual(1, item.activity_action_object.all().count())

        activity = self.desk.activity_stream.all()[0]
        self.assertEqual(activity.desk, self.desk)
        self.assertEqual(activity.actor, self.user)
        self.assertEqual(activity.verb, Activity.VERB_CREATED)
        self.assertEqual(activity.actor_email, '')
        self.assertEqual(activity.target, item)
        self.assertEqual(activity.action_object_str, '')
        self.assertIsNone(activity.action_object)

    def test_action_object_and_target(self):
        """Actor, verb, action object and target."""
        item = items_factories.ConfirmedItemFactory.create(desk=self.desk)
        create_activity(
            actor=self.user,
            desk=self.desk,
            verb=Activity.VERB_CREATED,
            target=item
        )

        # Test `activities_for`.
        self.assertEqual(1, Activity.activities_for(item, desk=self.desk).count())

        activity = self.desk.activity_stream.all()[0]
        self.assertEqual(activity.desk, self.desk)
        self.assertEqual(activity.actor, self.user)
        self.assertEqual(activity.verb, Activity.VERB_CREATED)
        self.assertEqual(activity.actor_email, '')
        self.assertEqual(activity.action_object_str, '')
        self.assertEqual(activity.target, item)

    def test_action_object_str(self):
        """Actor, verb, and action object string representation."""
        item = items_factories.ConfirmedItemFactory.create(desk=self.desk)
        create_activity(
            actor=self.user,
            desk=self.desk,
            verb=Activity.VERB_CREATED,
            target=item,
            action_object_str=item.number
        )

        # Test `activities_for`.
        self.assertEqual(1, Activity.activities_for(item, desk=self.desk).count())

        activity = self.desk.activity_stream.all()[0]
        self.assertEqual(activity.desk, self.desk)
        self.assertEqual(activity.actor, self.user)
        self.assertEqual(activity.verb, Activity.VERB_CREATED)
        self.assertEqual(activity.actor_email, '')
        self.assertIsNone(activity.action_object)
        self.assertEqual(activity.action_object_str, str(item.number))
        self.assertEqual(activity.target, item)


@skip("View obsoleted by the new Vue.js UI")
class ActivityStreamUiTest(PilotAdminUserMixin, TestCase):
    def test_activity_list(self):
        """Test activity list."""

        # Create some activities.
        activity_stream = activity_stream_factories.ActivityFactory.create_batch(
            size=30, desk=self.desk, actor=self.user)

        # Test GET.
        response = self.client.get(reverse('activity_stream'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(activity_stream), response.context['paginator'].count)

        # Create another desk.
        other_desk = desks_factories.DeskFactory.create()
        # Create some activities for the other desk.
        activity_stream_factories.ActivityFactory.create_batch(size=10, desk=other_desk)

        # Test GET.
        response = self.client.get(reverse('activity_stream'))
        self.assertEqual(response.status_code, 200)
        # The number of activities should still be the same.
        self.assertEqual(len(activity_stream), response.context['paginator'].count)
