import datetime
import random

import factory
import factory.fuzzy
from django.utils import timezone
from django.utils.timezone import make_naive

from pilot.channels.tests import factories as channels_factories
from pilot.desks.tests import factories as desks_factories
from pilot.items.models import EditSession, Item
from pilot.utils.test import prosemirror_body, ItemTypeTestingMixin


class ItemFactory(factory.DjangoModelFactory):
    """Base Item factory."""
    FACTORY_FOR = Item

    desk = factory.SubFactory(desks_factories.DeskFactory)
    item_type = factory.LazyAttribute(lambda item: item.desk.item_types.first())
    channel = factory.SubFactory(channels_factories.ChannelFactory, desk=factory.SelfAttribute('..desk'))
    created_by = factory.LazyAttribute(lambda item: item.desk.organization.created_by)
    publication_dt = factory.Sequence(lambda n: make_naive(timezone.now() + datetime.timedelta(days=1 + int(n))))
    workflow_state = factory.LazyAttribute(lambda item: item.desk.workflow_states.first())

    json_content = factory.Dict({
        'title': factory.Sequence("Item {0}".format),
        'body': factory.Sequence(lambda n: prosemirror_body("Content %03d" % n))
    })
    annotations = {}

    @factory.post_generation
    def state_name(self, create, extracted, **kwargs):
        if extracted:
            self.workflow_state = self.desk.workflow_states.get(name=extracted)

    @factory.post_generation
    def targets(self, create, extracted, **kwargs):
        """
        Add optional targets list, e.g.
            - ItemFactory.create(targets=[target1, target2])
            - item__targets=[target1, target2]
        """
        if extracted:
            # A list of targets were passed in, use them.
            for target in extracted:
                self.targets.add(target)

    @factory.post_generation
    def owners(self, create, extracted, **kwargs):
        """
        Add optional owners list, e.g.
            - ItemFactory.create(owners=[owner1, owner2])
            - item__owners=[owner1, owner2]
        """
        if extracted:
            # A list of owners were passed in, use them.
            for owner in extracted:
                self.owners.add(owner)

    @factory.post_generation
    def assets(self, create, extracted, **kwargs):
        """
        Add optional assets list, e.g.
            - ItemFactory.create(assets=[target1, target2])
            - item__assets=[target1, target2]
        """
        if extracted:
            # A list of assets were passed in, use them.
            for asset in extracted:
                self.assets.add(asset)

    # DjangoModelFactory will save a second time the model when any postgeneration hook has been run.
    # We have three hooks that may add targets, owners and assets to the created Item.
    # This situation will create two EditSessions, but we'd like to always have only one initial
    # EditSession to have consistent testing.
    # So we explicitely keep only the last snapshot done, and discard the others.
    @classmethod
    def _after_postgeneration(cls, item, create, results=None):
        factory.DjangoModelFactory._after_postgeneration(item, create, results)
        EditSession.objects.filter(item=item).exclude(pk=item.last_session.pk).delete()


class ConfirmedItemFactory(ItemFactory):
    """Confirmed Item factory e.g. an Item out of ideastorm states."""

    workflow_state = factory.LazyAttribute(lambda item: item.desk.workflow_states.get(
        name=random.choice([
            InitialStateNames.EDITION_READY,
            InitialStateNames.VALIDATION_READY,
            InitialStateNames.PUBLICATION_READY,
            InitialStateNames.PUBLISHED,
            InitialStateNames.UNPUBLISHED,
        ])
    ))

class ItemTweetFactory(ItemFactory):
    """An Item factory with an `item_type` set to TWITTER_TYPE."""
    @factory.lazy_attribute
    def item_type(self):
        return ItemTypeTestingMixin().get_item_type_twitter(self.desk)


class ItemFacebookFactory(ItemFactory):
    """An Item factory with an `item_type` set to FACEBOOK_TYPE."""
    @factory.lazy_attribute
    def item_type(self):
        return ItemTypeTestingMixin().get_item_type_facebook(self.desk)


class ConfirmedItemTweetFactory(ConfirmedItemFactory):
    """Confirmed Item factory with an `item_type` set to TWITTER_TYPE."""
    @factory.lazy_attribute
    def item_type(self):
        return ItemTypeTestingMixin().get_item_type_twitter(self.desk)


class ConfirmedItemFacebookFactory(ConfirmedItemFactory):
    """Confirmed Item factory with an `item_type` set to TWITTER_TYPE."""
    @factory.lazy_attribute
    def item_type(self):
        return ItemTypeTestingMixin().get_item_type_facebook(self.desk)


class EditSessionFactory(factory.DjangoModelFactory):
    """Base EditSession factory."""
    FACTORY_FOR = EditSession

    # We pass in session=None to prevent ItemFactory from creating another session
    # (this disables the RelatedFactory).
    item = factory.SubFactory(ItemFactory,
                              json_content=factory.SelfAttribute('..json_content'),
                              annotations=factory.SelfAttribute('..annotations'))
    content_schema = factory.LazyAttribute(lambda snapshot: snapshot.item.content_schema)
    created_by = factory.LazyAttribute(lambda session: session.item.created_by)
    json_content = factory.Dict({
        'title': factory.Sequence("Item From Snapshot {0}".format),
        'body': factory.Sequence(lambda n: prosemirror_body("Content From Snapshot %03d" % n))
    })
    annotations = None


class ReviewFactory(factory.DjangoModelFactory):
    """Base Review factory."""
    FACTORY_FOR = Review

    session = factory.SubFactory(EditSessionFactory)
    created_by = factory.LazyAttribute(lambda review: review.session.created_by)
    email = factory.Sequence("john.smith{0}@example.com".format)


class SavedFilterFactory(factory.DjangoModelFactory):
    """Base SavedFilter factory."""
    FACTORY_FOR = SavedFilter

    desk = factory.SubFactory(desks_factories.DeskFactory)
    user = factory.LazyAttribute(lambda item: item.desk.organization.created_by)
    title = factory.Sequence("Item Saved Filter {0}".format)
    filter = factory.LazyAttribute(lambda item: "workflow_state={0}".format(
        random.choice([state.id for state in item.desk.workflow_states.all()])))


class PublicSharedFilterFactory(factory.DjangoModelFactory):
    """Base PublicSharedFilter factory."""
    FACTORY_FOR = PublicSharedFilter

    saved_filter = factory.SubFactory(SavedFilterFactory)
    email = factory.Sequence("john.smith{0}@example.com".format)
