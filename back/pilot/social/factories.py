import datetime

from django.utils import timezone

import factory

from pilot.items.tests import factories as items_factories
from pilot.social.models import FacebookLog, TweetLog


class FacebookLogFactory(factory.DjangoModelFactory):
    """ Factory for ItemType."""
    FACTORY_FOR = FacebookLog

    item = factory.SubFactory(items_factories.ItemFacebookFactory)
    text = factory.Sequence("Custôm typé name {0}".format)
    status_dt = factory.Sequence(lambda n: timezone.now() + datetime.timedelta(days=1 + int(n)))


class TweetLogFactory(factory.DjangoModelFactory):
    """ Factory for ItemType."""
    FACTORY_FOR = TweetLog

    item = factory.SubFactory(items_factories.ItemTweetFactory)
    text = factory.Sequence("Custôm typé name {0}".format)
    tweet_dt = factory.Sequence(lambda n: timezone.now() + datetime.timedelta(days=1 + int(n)))
