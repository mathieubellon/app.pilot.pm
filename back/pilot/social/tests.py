import datetime
from unittest.case import skip

from django.test import TestCase
from django.utils.encoding import smart_str
from django.utils import timezone

from pilot.channels.tests.factories import ChannelFactory
from pilot.item_types import initial_item_types
from pilot.utils.test import PilotAdminUserMixin
from pilot.workflow.initial_states import InitialStateNames

from pilot.social.factories import FacebookLogFactory, TweetLogFactory
from pilot.social.models import FacebookLog, TweetLog
from management.commands.stats_facebook import Command as FacebookCommand
from management.commands.stats_tweets import Command as TwitterCommand


@skip("Social features disabled for now")
class FactoriesTests(TestCase):
    """Test FacebookLog Factories."""

    def test_facebooklog_factory(self):
        """Test FacebookLogFactory."""
        facebook_log = FacebookLogFactory.create()
        self.assertEqual(facebook_log.item.item_type, initial_item_types.FACEBOOK_TYPE)

    def test_unicode_on_facebook_log(self):
        unicode_text = "L’AEK Athènes FC (en grec : Αθλητική Ένωσις Κωνσταντινουπόλεως"
        facebook_item = FacebookLogFactory.create(text=smart_str(unicode_text))
        created_item = FacebookLog.objects.get(pk=facebook_item.pk)
        self.assertEqual(created_item.text, unicode_text)

    def test_tweetlog_factory(self):
        """Test TweetLogFactory."""
        tweet_log = TweetLogFactory.create()
        self.assertEqual(tweet_log.item.item_type, initial_item_types.TWITTER_TYPE)

    def test_unicode_on_twitter_log(self):
        unicode_text = "L’AEK Athènes FC (en grec : Αθλητική Ένωσις Κωνσταντινουπόλεως"
        tweet_log = TweetLogFactory.create(text=smart_str(unicode_text))
        created_item = TweetLog.objects.get(pk=tweet_log.pk)
        self.assertEqual(created_item.text, unicode_text)


@skip("Social features disabled for now")
class ModelTests(PilotAdminUserMixin, TestCase):
    def test_info_field(self):
        log = TweetLogFactory.create(
            item__state_name=InitialStateNames.PUBLISHED,
        )
        json_dict = {'key1': 'foo', 'key2': 'bar', 'list_key': [1, 2, 3]}
        log.info = json_dict
        log.save()
        self.assertEqual(log.info['key1'], json_dict['key1'])
        self.assertEqual(log.info['list_key'][1], json_dict['list_key'][1])

    def test_facebook_log_info_field(self):
        log = FacebookLogFactory.create(
            item__state_name=InitialStateNames.PUBLISHED,
        )
        json_dict = {'key1': 'foo', 'key2': 'bar', 'list_key': [1, 2, 3]}
        log.info = json_dict
        log.save()
        self.assertEqual(log.info['key1'], json_dict['key1'])
        self.assertEqual(log.info['list_key'][1], json_dict['list_key'][1])


@skip("Social features disabled for now")
class FacebookManagementTests(PilotAdminUserMixin, TestCase):
    def test_get_queryset(self):
        channel = ChannelFactory.create(desk=self.desk)
        FacebookLogFactory.create_batch(
            size=5,
            item__channel=channel,
            item__state_name=InitialStateNames.PUBLISHED,
        )
        FacebookLogFactory.create_batch(
            size=5,
            item__channel=channel,
            item__state_name=InitialStateNames.PUBLISHED,
        )
        FacebookLogFactory.create_batch(
            size=5,
            item__channel=channel,
            item__state_name=InitialStateNames.PUBLISHED,
            item__desk=self.desk
        )
        for day in range(1, 6):
            FacebookLogFactory.create(
                item__channel=channel,
                item__state_name=InitialStateNames.PUBLISHED,
                item__desk=self.desk,
                last_checked=timezone.now() - datetime.timedelta(days=day)
            )
        c = FacebookCommand()
        c.older_tweets = False
        queryset = c._get_queryset(self.desk, channel)

        # Only items with channel and desk
        self.assertEqual(len(queryset), 10)
        for t in queryset:
            self.assertTrue(t in queryset)

        # checking that the 5 first items have a None `last_checked` value
        for i in range(0, 5):
            self.assertEqual(queryset[i].last_checked, None)

        # checking that the 5 last items are ordered according to `last_checked` value
        for i in range(5, 9):
            self.assertTrue(queryset[i + 1].last_checked > queryset[i].last_checked)

@skip("Social features disabled for now")
class TwitterManagementTests(PilotAdminUserMixin, TestCase):
    def test_get_queryset(self):
        channel = ChannelFactory.create(desk=self.desk)
        TweetLogFactory.create_batch(
            size=5,
            item__channel=channel,
            item__state_name=InitialStateNames.PUBLISHED,
        )
        TweetLogFactory.create_batch(
            size=5,
            item__channel=channel,
            item__state_name=InitialStateNames.PUBLISHED,
        )
        TweetLogFactory.create_batch(
            size=5,
            item__channel=channel,
            item__state_name=InitialStateNames.PUBLISHED,
            item__desk=self.desk
        )
        for day in range(1, 6):
            TweetLogFactory.create(
                item__channel=channel,
                item__state_name=InitialStateNames.PUBLISHED,
                item__desk=self.desk,
                last_checked=timezone.now() - datetime.timedelta(days=day)
            )
        c = TwitterCommand()
        c.older_tweets = False
        queryset = c._get_queryset(self.desk, channel)

        # Only items with channel and desk
        self.assertEqual(len(queryset), 10)
        for t in queryset:
            self.assertTrue(t in queryset)

        # checking that the 5 first items have a None `last_checked` value
        for i in range(0, 5):
            self.assertEqual(queryset[i].last_checked, None)

        # checking that the 5 last items are ordered according to `last_checked` value
        for i in range(5, 9):
            self.assertTrue(queryset[i + 1].last_checked > queryset[i].last_checked)
