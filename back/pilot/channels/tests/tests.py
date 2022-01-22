from django.test import TestCase

from pilot.channels.tests import factories as channels_factories
from pilot.desks.tests import factories as desks_factories
from pilot.utils import states


class FactoriesTests(TestCase):
    def test_channel_factory(self):
        """Test ChannelFactory."""
        channel = channels_factories.ChannelFactory.create()
        self.assertIsNotNone(channel.desk)
        self.assertIsNone(channel.parent)
        self.assertIsNone(channel.closed_at)
        self.assertEqual(channel.owners.count(), 0)
        self.assertEqual(channel.created_by, channel.desk.organization.created_by)
        self.assertEqual(channel.state, states.STATE_ACTIVE)
        self.assertIsNone(channel.updated_by)

    def test_twitterchannel_factory(self):
        """Test TwitterChannelFactory."""
        channel = channels_factories.TwitterChannelFactory.create()
        self.assertIsNotNone(channel.desk)
        self.assertIsNone(channel.closed_at)
        self.assertEqual(channel.owners.count(), 0)
        self.assertEqual(channel.created_by, channel.desk.organization.created_by)
        self.assertEqual(channel.state, states.STATE_ACTIVE)
        self.assertEqual(channel.type.publication_target, ChannelType.PublicationTarget.TWITTER)
        self.assertIsNone(channel.updated_by)

    def test_facebookchannel_factory(self):
        """Test FacebookChannelFactory."""
        channel = channels_factories.FacebookChannelFactory.create()
        self.assertIsNotNone(channel.desk)
        self.assertIsNone(channel.closed_at)
        self.assertEqual(channel.owners.count(), 0)
        self.assertEqual(channel.created_by, channel.desk.organization.created_by)
        self.assertEqual(channel.state, states.STATE_ACTIVE)
        self.assertEqual(channel.type.publication_target, ChannelType.PublicationTarget.FACEBOOK)
        self.assertIsNone(channel.updated_by)

    def test_channeltoken_factory(self):
        """Test ChannelTokenFactory."""

        channeltoken = channels_factories.ChannelTokenFactory.create()
        self.assertIsNotNone(channeltoken.channel)


class ChannelModelTests(TestCase):
    def test_managers(self):
        """
        Test Channel managers:
        - Channel.objects
        - Channel.active_objects
        - Channel.closed_objects
        """

        TOTAL_CHANNELS = 100

        desk = desks_factories.DeskFactory.create()
        channels = channels_factories.ChannelFactory.create_batch(size=TOTAL_CHANNELS, desk=desk)

        # Close the latter half of channels.
        for channel in channels[TOTAL_CHANNELS / 2:]:
            channel.close()

        self.assertEqual(Channel.objects.all().count(), TOTAL_CHANNELS)
        self.assertEqual(Channel.active_objects.all().count(), TOTAL_CHANNELS / 2)
        self.assertEqual(Channel.closed_objects.all().count(), TOTAL_CHANNELS / 2)


class ChannelWorkflowTests(TestCase):
    """Test Channel workflow."""

    def test_close(self):
        """Create a Channel then close it."""

        channel = channels_factories.ChannelFactory.create()
        self.assertIsNone(channel.closed_at)

        # Close the channel.
        channel.close(user=channel.created_by)
        self.assertEqual(channel.state, states.STATE_CLOSED)
        self.assertIsNotNone(channel.closed_at)
        self.assertEqual(channel.updated_by, channel.created_by)


class ChannelTokenModelTests(TestCase):
    """Test channel token model."""

    def test_generate(self):
        """Create a channel token and check if key was generated"""

        channeltoken = channels_factories.ChannelTokenFactory.create()
        self.assertIsNotNone(channeltoken.key)

    def test_save(self):
        """Ensure that saving a chanel token doesn't generate a new key"""

        channeltoken = channels_factories.ChannelTokenFactory.create()
        key = channeltoken.key

        channeltoken.save()

        self.assertEqual(key, channeltoken.key)


class ChannelHierarchyTests(TestCase):
    """Test channel parents and hierarchy."""

    def setUp(self):
        self.grandparent = channels_factories.ChannelFactory.create(name='gp')
        self.parent = channels_factories.ChannelFactory.create(name='p', parent=self.grandparent)
        self.child = channels_factories.ChannelFactory.create(name='c', parent=self.parent)

    def tearDown(self):
        Channel.objects.all().delete()

    def test_parent_subchannels(self):
        """Ensure parent and subchannels can be queried."""
        self.assertEqual(self.parent, self.child.parent)
        self.assertIn(self.child, self.parent.subchannels.all())

    def test_parent_deletion(self):
        """Ensure deleting a parent does not delete subchannels."""
        self.parent.delete()
        all_channels = Channel.objects.all()
        self.assertIn(self.child, all_channels)
        self.assertIsNone(all_channels.get(pk=self.child.pk).parent)

    def test_prevent_child_as_parent(self):
        """Ensure a Channel cannot have one of its children as parent."""
        from mptt.exceptions import InvalidMove
        self.parent.parent = self.child
        self.assertRaises(InvalidMove, self.parent.save)

    def test_channel_representation_contains_parents_names(self):
        """Ensure hierarchy field is correctly filled with parents"""
        self.assertEqual(str(self.grandparent), str(self.grandparent.name))
        self.assertEqual(str(self.parent), '{0} / {1}'.format(self.grandparent.name,
                                                                  self.parent.name))

    def test_channel_representation_is_refreshed_by_descendant(self):
        expected = '{0} / {1} / {2}'.format(self.grandparent.name,
                                            self.parent.name,
                                            self.child.name)
        self.assertEqual(str(self.child), expected)

        self.parent.parent = None
        self.parent.save()
        child = Channel.objects.get(pk=self.child.pk)
        self.assertNotEqual(str(child), expected)

    def test_channel_representation_is_refreshed_by_ascendant(self):
        newgrandparent = channels_factories.ChannelFactory.create(name='nwp')
        self.parent.parent = newgrandparent
        self.parent.save()
        child = Channel.objects.get(pk=self.child.pk)
        self.assertIn(str(newgrandparent), str(child))
        self.assertNotIn(str(self.grandparent), str(child))

    def test_channels_are_ordered_by_level_hierarchy(self):
        """Ensure the channel hierarchy is respected."""
        SIZE = 20
        channels = channels_factories.ChannelFactory.create_batch(size=SIZE)
        channels_pks = [channel.pk for channel in channels]

        for i, channel in enumerate(channels[:SIZE / 2]):
            parent = channels[i + SIZE / 2]
            channel.parent = parent
            channel.save()

        ordered_channels = [c for c in Channel.objects.all() if c.pk in channels_pks]

        for i, channel in enumerate(ordered_channels):
            if i % 2 == 0:
                self.assertIsNone(channel.parent)
            else:
                self.assertIsNotNone(channel.parent)
