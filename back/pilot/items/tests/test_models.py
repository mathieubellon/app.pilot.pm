from unittest import skip

from django.db.models import Q, ProtectedError
from django.test import TestCase
from django.utils import timezone

from pilot.pilot_users.tests import factories as users_factories
from pilot.assets.tests import factories as assets_factories
from pilot.projects.tests import factories as projects_factories
from pilot.utils import pilot_languages, states
from pilot.desks.tests import factories as desks_factories
from pilot.items.tests import factories as items_factories
from pilot.item_types import initial_item_types
from pilot.targets.tests import factories as targets_factories
from pilot.utils.models import get_fields_to_serialize, serialize_model_instance
from pilot.utils.test import WorkflowStateTestingMixin, prosemirror_body, ItemTypeTestingMixin
from pilot.item_types.tests import factories as item_types_factories


class FactoriesTests(ItemTypeTestingMixin, WorkflowStateTestingMixin, TestCase):
    """Test Item Factories."""

    def test_item_type_factory(self):
        """Test ItemTypeFactory."""
        item_type = item_types_factories.ItemTypeFactory.create()
        self.assertIsNotNone(item_type.desk)

        item = items_factories.ItemFactory.create()

        # We assign a custom type to item model.
        item.item_type = item_type
        item.save()

        # We check that item_type are updated.
        self.assertEqual(item.item_type, item_type)

        # Cannot delete the item_type because the cascade protection on ItemType -> Item
        with self.assertRaises(ProtectedError):
            item_type.delete()

    def test_item_factory(self):
        """Test ItemFactory."""
        target = targets_factories.TargetFactory.create()
        owner = users_factories.PilotUserFactory()

        item = items_factories.ItemFactory.create(targets=[target], owners=[owner])

        # Refresh the cached item instance to ensure to fetch the RelatedFactory results.
        item = Item.objects.get(pk=item.pk)

        self.assertIsNotNone(item.desk)
        self.assertIsNotNone(item.channel)
        self.assertEqual(item.targets.count(), 1)
        self.assertEqual(item.owners.count(), 1)
        self.assertEqual(item.owners.all()[0], owner)

        self.assertIsNotNone(item.guidelines)
        self.assertIsNotNone(item.where)
        self.assertIsNotNone(item.goal)
        self.assertIsNotNone(item.contacts)
        self.assertIsNotNone(item.sources)

        self.assertEqual(1, item.number)

        self.assertEqual(item.workflow_state, self.get_state_edition_ready(item.desk))

        self.assertIsNotNone(item.created_at)
        self.assertIsNotNone(item.updated_at)
        self.assertIsNotNone(item.publication_dt)

        self.assertIsNotNone(item.item_type)

        self.assertEqual(item.created_by, item.desk.created_by)
        self.assertEqual(item.created_by, item.channel.created_by)
        self.assertEqual(item.created_by, item.desk.organization.created_by)
        self.assertEqual(item.created_by_external_email, '')
        self.assertEqual(1, item.desk.organization.users.all().count())

        # Check the EditSession creation result.
        self.assertEqual(1, EditSession.objects.filter(item=item).count())
        self.assertTrue(EditSession.objects.get(item=item))
        session = EditSession.objects.get(item=item)
        self.assertEqual(item, session.item)

        self.assertEqual(item.title, session.title)
        self.assertEqual(item.content['body'], session.content['body'])
        self.assertEqual(item.created_by, session.created_by)
        self.assertDictEqual(item.content, session.content)
        self.assertListEqual(item.content_schema, session.content_schema)

        self.assertFalse(item.external_publication_error)
        self.assertIsNone(item.language)

    def test_get_languages_abbr(self):
        # Item without language
        item_without_lang = items_factories.ItemFactory.create()
        # Refresh the cached item instance to ensure to fetch the RelatedFactory results.
        item_without_lang = Item.objects.get(pk=item_without_lang.pk)
        self.assertEqual(item_without_lang.language, None)
        self.assertEqual(item_without_lang.get_language_abbr(), "Aucun")

        # Item with language
        lang = pilot_languages.LANGUAGES.keys()[0]
        item_with_lang = items_factories.ItemFactory.create(language=lang)
        # Refresh the cached item instance to ensure to fetch the RelatedFactory results.
        item_with_lang = Item.objects.get(pk=item_with_lang.pk)
        self.assertEqual(item_with_lang.language, lang)
        self.assertEqual(item_with_lang.get_language_abbr(), lang[:2])

    def test_item_idea_factory(self):
        """Test ItemIdeaFactory."""
        item = items_factories.ItemIdeaFactory.create()
        self.assertEqual(item.idea_state, states.STATE_IDEA)
        self.assertNotEqual('', item.title)

    def test_session_factory(self):
        """Test EditSessionFactory."""
        session = items_factories.EditSessionFactory.create()

        self.assertIsNotNone(session.item)

        self.assertIsNone(session.restored_from)

        self.assertIsNotNone(session.title)
        self.assertIsNotNone(session.content['body'])

        self.assertEqual('', session.comment)

        self.assertIsNotNone(session.version)
        self.assertIsNotNone(session.created_by)
        self.assertIsNotNone(session.created_at)

        item = session.item
        self.assertEqual(session.created_by, item.created_by)
        self.assertDictEqual(item.content, session.content)
        self.assertListEqual(item.content_schema, session.content_schema)
        self.assertEqual(item.annotations, session.annotations)

        # Initial snapshot + the one we just created
        self.assertEqual(2, EditSession.objects.filter(item=item).count())

    def test_review_factory(self):
        """Test ReviewFactory."""
        review = items_factories.ReviewFactory.create()

        self.assertIsNotNone(review.session)
        self.assertIsNotNone(review.created_by)

        self.assertEqual(review.session.created_by, review.created_by)

        self.assertIsNotNone(review.created_at)

        self.assertEqual('', review.comment)

        self.assertIsNotNone(review.email)
        self.assertIsNotNone(review.token)

        self.assertEqual('', review.password)

        self.assertEqual(review.status, Review.STATUS_PENDING)

        self.assertEqual('', review.review_comment)

        self.assertIsNone(review.reviewed_at)

        self.assertEqual(False, review.is_editable)

    def test_saved_filter_factory(self):
        """Test SavedFilterFactory."""
        saved_filter = items_factories.SavedFilterFactory.create()

        self.assertIsNotNone(saved_filter.desk)
        self.assertIsNotNone(saved_filter.user)
        self.assertIsNotNone(saved_filter.title)
        self.assertIsNotNone(saved_filter.query)
        self.assertIsNotNone(saved_filter.created_at)

        self.assertEqual(saved_filter.type, SavedFilter.TYPE_CALENDAR)
        self.assertEqual(saved_filter.user, saved_filter.desk.created_by)

    def test_public_shared_filter_factory(self):
        """Test PublicSharedFilterFactory."""
        shared_filter = items_factories.PublicSharedFilterFactory.create()

        self.assertIsNotNone(shared_filter.saved_filter)
        self.assertIsNotNone(shared_filter.email)
        self.assertIsNotNone(shared_filter.token)
        self.assertIsNotNone(shared_filter.created_at)

        self.assertEqual('', shared_filter.password)

        self.assertEqual(shared_filter.saved_filter.user, shared_filter.saved_filter.desk.created_by)


class ItemModelTests(TestCase, ItemTypeTestingMixin):
    """Test Item Model."""

    def tearDown(self):
        # Delete all Item objects after each test.
        Item.objects.all().delete()

    def test_number(self):
        """Test Item number field."""

        desk = desks_factories.DeskFactory.create()
        items = items_factories.ItemFactory.create_batch(size=100, desk=desk)

        for i, item in zip(range(1, 101), items):
            self.assertEqual(i, item.number)

        # Ensure that we have 100 items.
        self.assertEqual(100, Item.objects.all().count())

        # Delete all Item objects.
        Item.objects.all().delete()

        # Ensure that we have now 0 items.
        self.assertEqual(0, Item.objects.all().count())

        # Create a new item.
        item = items_factories.ItemFactory.create(desk=desk)
        self.assertEqual(1, Item.objects.all().count())
        # The new item should have the number #101.
        self.assertEqual(101, item.number)
        self.assertEqual(101, ItemStats.objects.get(desk=desk).items_created_num)

    def test_visibility(self):
        """Test Item number field."""

        desk = desks_factories.DeskFactory.create()
        items_factories.ItemFactory.create_batch(size=22, desk=desk)  # visible items
        items_factories.ItemFactory.create_batch(
            size=25,
            desk=desk,
            in_trash=True)  # in trash items
        items_factories.ItemFactory.create_batch(
            size=27,
            desk=desk,
            hidden=True)  # hidden items

        # Ensure that we have 22 items.
        visible_items = Item.objects.all()
        self.assertEqual(22, visible_items.count())

        # Putting an item into trash and ensuring we have one item less.
        item = visible_items[0]
        item.put_in_trash()
        visible_items = Item.objects.all()
        self.assertEqual(21, visible_items.count())

    def test_fk_on_delete(self):
        """Test ForeignKey.on_delete."""

        desk = desks_factories.DeskFactory.create()
        project = projects_factories.ProjectFactory.create(desk=desk)
        target = targets_factories.TargetFactory.create()
        item = items_factories.ConfirmedItemFactory.create(desk=desk, project=project, targets=[target])

        self.assertIsNotNone(item.channel)
        self.assertEqual(item.targets.count(), 1)
        self.assertIsNotNone(item.project)

        item.channel.delete()
        item.targets.all()[0].delete()
        item.project.delete()

        # Item should still exists.
        item = Item.confirmed_objects.get(pk=item.pk)
        self.assertIsNone(item.channel)
        self.assertEqual(item.targets.count(), 0)
        self.assertIsNone(item.project)

        # Cannot delete the desk because the cascade protection on ItemType -> Item
        with self.assertRaises(ProtectedError):
            desk.delete()

    def test_get_item(self):
        desks_factories.DeskFactory.create()
        item_type = item_types_factories.ItemTypeFactory()
        item1 = items_factories.ItemFactory()
        item2 = items_factories.ItemTweetFactory()
        item3 = items_factories.ItemFactory(item_type=item_type)

        self.assertEqual(item1.item_type.name, initial_item_types.InitialItemTypeNames.ARTICLE)
        self.assertEqual(item2.item_type.name, initial_item_types.InitialItemTypeNames.TWITTER)
        self.assertEqual(item3.item_type, item_type)

    @skip("Social features disabled for now")
    def test_get_external_publication_error(self):
        """Test `get_external_publication_error` method."""

        item = items_factories.ItemTweetFactory.create()
        self.assertIsNone(item.get_external_publication_error())

        item = items_factories.ItemTweetFactory.create(
            external_publication_error="'{malforméd 'json"
        )
        self.assertEqual(item.get_external_publication_error(), [{'message': "Erreur indéfinie"}])

    @skip("Social features disabled for now")
    def test_tweet_can_publish_now(self):
        """Test `can_publish_now` method."""

        item = items_factories.ItemTweetFactory.create(channel=None)
        self.assertFalse(item.can_publish_now)

        item = items_factories.ItemTweetFactory.create(channel__type__publication_target="")
        self.assertFalse(item.can_publish_now)

    @skip("Social features disabled for now")
    def test_too_long_tweet(self):
        """Test `get_instant_publication_warnings` method."""
        # Twitter item with 200 chars
        st = "é$" * 100
        item = items_factories.ItemTweetFactory.create()
        item.content['body'] = st
        item.save()
        self.assertEqual(
            str(item.get_instant_publication_warnings()[0]['message']),
            "Le contenu est trop long pour le type choisi."
        )

    # Managers
    def test_confirmed_item_manager(self):
        """Test ConfirmedItemManager."""

        desk = desks_factories.DeskFactory.create()
        items_factories.ItemFactory.create(
            desk=desk,
            in_trash=True)  # trashed items
        items_factories.ItemFactory.create(
            desk=desk,
            hidden=True)  # hidden items
        # Create 1 Item for each existing WorkflowState.
        for s in desk.workflow_states.all():
            items_factories.ItemFactory.create(workflow_state=s, desk=desk)
        for s in states.IN_IDEA_STATES:
            items_factories.ItemIdeaFactory.create(idea_state=s, desk=desk)

        # The default manager must returns all visible items.
        self.assertEqual(
            Item.objects.all().count(),
            desk.workflow_states.count() + len(states.IN_IDEA_STATES)
        )
        idea_states = Item.objects.all().values_list('idea_state', flat=True)
        self.assertIn(states.STATE_IDEA, idea_states)
        self.assertIn(states.STATE_REJECTED, idea_states)

        # The confirmed_objects manager should returns all visible items except the
        # `idea` and `rejected` status.
        self.assertEqual(
            Item.confirmed_objects.all().count(),
            desk.workflow_states.count()
        )
        confirmed_states = Item.confirmed_objects.all().values_list('idea_state', flat=True)
        self.assertNotIn(states.STATE_IDEA, confirmed_states)
        self.assertNotIn(states.STATE_REJECTED, confirmed_states)
        self.assertNotIn(states.STATE_ACCEPTED, confirmed_states)

    def test_in_trash_item_manager(self):
        """Test InTrashItemManager."""

        items_factories.ItemFactory.create_batch(8)
        in_trash_items = items_factories.ItemFactory.create_batch(
            9,
            in_trash=True
        )
        items_factories.ItemFactory.create_batch(7, hidden=True)

        # sanity check
        for item in in_trash_items:
            self.assertEqual(item.visibility, in_trash=True)
        # Only items in trash
        self.assertEqual(Item.in_trash_objects.all().count(), 9)

    def test_hidden_item_manager(self):
        """Test HiddenItemManager."""

        items_factories.ItemFactory.create_batch(8)
        items_factories.ItemFactory.create_batch(9, in_trash=True)
        hidden_items = items_factories.ItemFactory.create_batch(
            7,
            hidden=True
        )

        # sanity check
        for item in hidden_items:
            self.assertEqual(item.visibility, items_workflows.STATE_HIDDEN)
        # Only hidden items
        self.assertEqual(Item.all_the_objects.filter(hidden=True).count(), 7)

    def test_all_item_manager(self):
        """Test AllItemManager."""

        items_factories.ItemFactory.create_batch(8)
        items_factories.ItemFactory.create_batch(9, in_trash=True)
        items_factories.ItemFactory.create_batch(
            7,
            hidden=True
        )
        # Only hidden items
        self.assertEqual(Item.all_the_objects.all().count(), 24)

    def test_idea_item_manager(self):
        """Test IdeaItemManager."""
        items_factories.ItemFactory.create()
        items_factories.ItemIdeaFactory.create()
        self.assertEqual(Item.objects.all().count(), 2)
        self.assertEqual(Item.idea_objects.all().count(), 1)

    def test_get_metadata_fields_to_serialize(self):
        item = items_factories.ItemFactory.create()
        # updated_at, content and annotations should not appear in the metadata
        self.assertSetEqual(set(get_fields_to_serialize(item, item.NON_METADATA_FIELDS)), set((
            'photographer_needed', 'project', 'guidelines', 'sources', 'targets',
            'photo_investigations_needed',
            'goal', 'contacts', 'created_by', 'id', 'idea_state',
            'external_publication_error', 'scope', 'channel', 'updated_by', 'tags',
            'created_by_external_email', 'visibility', 'number', 'support_needed', 'desk',
            'item_type', 'created_by_external_token', 'owners', 'assets', 'language', 'item_type',
            'created_at', 'available_pictures', 'where', 'investigations_needed', 'mappings', 'is_private',
            'workflow_state')
        ))

    def test_get_serialized_metadata(self):
        project = projects_factories.ProjectFactory()
        target = targets_factories.TargetFactory()
        owner = users_factories.PilotUserFactory()
        asset = assets_factories.AssetFactory()
        item = items_factories.ItemFactory.create(
            project=project,
            targets=[target],
            owners=[owner],
            assets=[asset]
        )
        metadata = serialize_model_instance(item, item.NON_METADATA_FIELDS)
        self.assertEqual(metadata['pk'], item.pk)
        self.assertEqual(metadata['model'], 'items.item')

        fields = metadata['fields']
        self.assertNotIn('updated_at', fields)
        self.assertNotIn('json_content', fields)
        self.assertNotIn('annotations', fields)

        self.assertEqual(fields['project'], project.pk)
        self.assertEqual(fields['guidelines'], item.guidelines)
        self.assertEqual(fields['number'], item.number)
        self.assertEqual(fields['sources'], item.sources)
        self.assertEqual(fields['goal'], item.goal)
        self.assertEqual(fields['contacts'], item.contacts)
        self.assertEqual(fields['created_by'], item.created_by.pk)
        self.assertEqual(fields['workflow_state'], item.workflow_state.id)
        self.assertEqual(fields['photographer_needed'], item.photographer_needed)
        self.assertEqual(fields['external_publication_error'], item.external_publication_error)
        self.assertEqual(fields['scope'], item.scope)
        self.assertEqual(fields['channel'], item.channel.pk)
        self.assertEqual(fields['updated_by'], item.updated_by)
        self.assertEqual(fields['created_by_external_email'], item.created_by_external_email)
        self.assertEqual(fields['visibility'], item.visibility)
        self.assertEqual(fields['photo_investigations_needed'], item.photo_investigations_needed)
        self.assertEqual(fields['support_needed'], item.support_needed)
        self.assertEqual(fields['desk'], item.desk.pk)
        self.assertEqual(fields['item_type'], item.item_type.id)
        self.assertEqual(fields['created_by_external_token'], item.created_by_external_token)
        self.assertEqual(fields['language'], item.language)
        self.assertEqual(fields['available_pictures'], item.available_pictures)
        self.assertEqual(fields['where'], item.where)
        self.assertEqual(fields['investigations_needed'], item.investigations_needed)
        self.assertEqual(fields['mappings'], item.mappings)
        self.assertEqual(fields['is_private'], item.is_private)

        self.assertEqual(fields['targets'], [target.pk])
        self.assertEqual(fields['owners'], [owner.pk])
        self.assertEqual(fields['assets'], [asset.pk])


    def test_item_take_snapshot(self):
        item = items_factories.ItemFactory.create()

        # Initial snapshot
        self.assertEqual(1, item.sessions.count())

        # Content updated
        item.content = {'title': '1', 'body': prosemirror_body('1')}
        item.save()
        # A snapshot has been created
        self.assertEqual(2, item.sessions.count())

        # Metadata updated
        item.goal = "New goal"
        item.save()
        # A snapshot has been created
        self.assertEqual(3, item.sessions.count())

        # Annotations updated
        item.annotations = [{'fake': 'annotation'}]
        item.save()
        # A snapshot has been created
        self.assertEqual(4, item.sessions.count())

        # The saved data should be correct
        last_session = item.last_session
        self.assertDictEqual(item.content, last_session.content)
        self.assertListEqual(item.content_schema, last_session.content_schema)
        self.assertListEqual(item.annotations, last_session.annotations)
        self.assertDictEqual(serialize_model_instance(item, item.NON_METADATA_FIELDS), last_session.metadata)

        item.save()
        # Nothing is modified : no snapshot created
        self.assertEqual(4, item.sessions.count())

        # Only updated_at has been modified : no snapshot created
        item.updated_at = timezone.now()
        item.save()
        self.assertEqual(4, item.sessions.count())

        # We explicitely ask to not create a snapshot
        item.content = {'title': '2', 'body': prosemirror_body('2')}
        item.save(take_snapshot=False)
        self.assertEqual(4, item.sessions.count())

        # Check that the snapshot comment is saved
        self.assertEqual(5, item.sessions.count())

    def test_restore_content(self):
        item = items_factories.ItemFactory.create()

        # There's an initial snapshot
        self.assertEqual(1, item.sessions.count())

        # Create another version
        first_content = {
            'title': 'Awesome title',
            'body': prosemirror_body('Awesome body'),
        }
        item.content = first_content
        item.save()
        # A snapshot has been created
        self.assertEqual(2, item.sessions.count())
        first_content_snapshot = item.last_session
        self.assertDictEqual(item.content, first_content)
        self.assertDictEqual(first_content_snapshot.content, first_content)

        # Create another version
        second_content = {
            'title': 'Mighty title',
            'body': prosemirror_body('Mighty body'),
        }
        item.content = second_content
        item.save()
        # A snapshot has been created
        self.assertEqual(3, item.sessions.count())

        self.assertDictEqual(item.content, second_content)
        self.assertDictEqual(item.last_session.content, second_content)

        # Now restore the first content
        comment = 'Back to the past'
        item.restore_content(item.created_by, first_content_snapshot, comment=comment)

        # A snapshot has been created
        self.assertEqual(4, item.sessions.count())

        self.assertDictEqual(item.content, first_content)
        self.assertDictEqual(item.last_session.content, first_content)
        self.assertEqual(item.last_session.comment, comment)
        self.assertEqual(item.last_session.restored_from, first_content_snapshot)


class ItemWorkflowTests(TestCase):
    """Test Item Workflow."""

    def test_create_in_edition_ready_state(self):
        item = items_factories.ItemFactory.create(state_name=InitialStateNames.EDITION_READY)
        self.assertEqual(item.workflow_state, item.desk.workflow_states.get(name=InitialStateNames.EDITION_READY))

class ItemVisibilityWorkflowTests(TestCase):
    """Test Item Visibility Workflow."""

    def test_put_in_trash(self):
        item = items_factories.ItemFactory.create()
        self.assertEqual(item.visibility, items_workflows.STATE_VISIBLE)
        item.put_in_trash(user=item.created_by)
        self.assertEqual(item.visibility, items_workflows.STATE_INTRASH)
        self.assertEqual(item.updated_by, item.created_by)

    def test_restore_from_trash(self):
        item = items_factories.ItemFactory.create(in_trash=True)
        self.assertEqual(item.visibility, items_workflows.STATE_INTRASH)
        item.restore_from_trash(user=item.created_by)
        self.assertEqual(item.visibility, items_workflows.STATE_VISIBLE)
        self.assertEqual(item.updated_by, item.created_by)

    def test_hide(self):
        item = items_factories.ItemFactory.create(in_trash=True)
        self.assertEqual(item.visibility, items_workflows.STATE_INTRASH)
        item.hide(user=item.created_by)
        item = Item.all_the_objects.filter(hidden=True).get(pk=item.pk)
        self.assertEqual(item.visibility, items_workflows.STATE_HIDDEN)
        self.assertEqual(item.updated_by, item.created_by)


class ItemTagsTests(TestCase):
    """Test Item tags."""

    def test_tags(self):
        desk1 = desks_factories.DeskFactory.create()
        item1 = items_factories.ConfirmedItemFactory.create(desk=desk1)
        item1.tags.add('tag1')
        self.assertEqual(1, item1.tags.all().count())

        desk2 = desks_factories.DeskFactory.create()
        item2 = items_factories.ConfirmedItemFactory.create(desk=desk2)
        item2.tags.add('tag1')
        item2.tags.add('tag2')
        self.assertEqual(2, item2.tags.all().count())

        self.assertEqual(1, desk1.items.filter(tags__name__in=['tag1']).count())
        self.assertEqual(1, desk2.items.filter(tags__name__in=['tag1']).count())

        # All tags on all projects.
        self.assertEqual(2, Item.objects.filter(tags__name__in=['tag1']).count())

        # Get all tags on a specific desk.
        self.assertEqual(1, Tag.objects.filter(Q(item__desk=desk1) | Q(project__desk=desk1)).distinct().count())


class EditSessionModelTests(WorkflowStateTestingMixin, TestCase):
    """Test EditSession Model."""

    def tearDown(self):
        # Delete all EditSession objects after each test.
        EditSession.objects.all().delete()

    def test_version(self):
        """Test the version number of EditSession instances."""

        session = items_factories.EditSessionFactory.create()
        self.assertEqual(1, session.major_version)
        self.assertEqual(0, session.minor_version)
        self.assertEqual('1.0', session.version)

        # Update `session` several times.
        for i in range(2, 11):
            session.save()
            self.assertEqual('1.0', session.version)
            self.assertEqual(1, session.major_version)
            self.assertEqual(0, session.minor_version)

        # Update a bunch of new `session` related to the same `item`.
        for i in range(1, 11):
            new_session = items_factories.EditSessionFactory.create(
                item=session.item)
            self.assertEqual('1.{}'.format(i), new_session.version)
            self.assertEqual(1, new_session.major_version)
            self.assertEqual(i, new_session.minor_version)

        # Upgrade the last version as major
        new_session.upgrade_major_version()
        self.assertEqual(2, new_session.major_version)
        self.assertEqual(0, new_session.minor_version)

        # Try to upgrade it again, but fails
        self.assertRaisesMessage(Exception,
                                 "Cannot upgrade a version that is already a new major version",
                                 new_session.upgrade_major_version)

        # Try to upgrade the first snapshot, that is not current version anymore :
        self.assertRaisesMessage(Exception,
                                 "Cannot upgrade a version that is not the current version",
                                 session.upgrade_major_version)


class ReviewTests(TestCase):
    """Test Review Model."""

    def tearDown(self):
        # Delete all Review objects after each test.
        Review.objects.all().delete()

    def test_unique_together_itemcontentversion_token(self):
        """Test that session and token fields are unique together."""

        session = items_factories.EditSessionFactory.create()
        reviews = items_factories.ReviewFactory.create_batch(
            size=20,
            session=session
        )

        tokens = [f.token for f in reviews]
        versions = [f.session for f in reviews]

        self.assertFalse(len(tokens) > len(set(tokens)))  # Ensure all elements in the list are unique.
        self.assertEqual(1, len(set(versions)))  # Ensure all elements in the list are related to the same version.

    def test_approve(self):
        """Test the approve() method."""
        review = items_factories.ReviewFactory.create()
        review.approve()
        self.assertEqual(review.status, Review.STATUS_APPROVED)
        self.assertIsNotNone(review.reviewed_at)

    def test_reject(self):
        """Test the reject() method."""
        review = items_factories.ReviewFactory.create()
        review.reject()
        self.assertEqual(review.status, Review.STATUS_REJECTED)
        self.assertIsNotNone(review.reviewed_at)


class PublicSharedFilterTests(TestCase):
    """Test PublicSharedFilter Model."""

    def test_unique_together_savedFilter_token(self):
        """Test that saved_filter and token fields are unique together."""

        saved_filter = items_factories.SavedFilterFactory.create(
            type=SavedFilter.TYPE_CALENDAR,
            filter='start=2013-09-29&end=2013-11-10&project=2&project=3'
        )

        shared_filters = items_factories.PublicSharedFilterFactory.create_batch(
            size=20, saved_filter=saved_filter, token='toto')

        tokens = [f.token for f in shared_filters]

        self.assertFalse(len(tokens) > len(set(tokens)))  # Ensure all elements in the list are unique.

    def test_token_after_update(self):
        """Test that the token is not changed after an update."""

        # Create a shared filter.
        shared_filter = items_factories.PublicSharedFilterFactory.create()
        first_token = shared_filter.token

        # Update the shared filter.
        shared_filter.save()

        # Fetch the updated shared filter.
        shared_filter = PublicSharedFilter.objects.get(pk=shared_filter.pk)
        new_token = shared_filter.token

        # The token must still be the same.
        self.assertEqual(first_token, new_token)


class ItemChannelFilterTests(TestCase):
    def setUp(self):
        self.item_parent = items_factories.ItemFactory.create()
        self.item_child = items_factories.ItemFactory.create()
        self.channel_child = self.item_child.channel
        self.channel_parent = self.item_parent.channel
        self.channel_child.parent = self.channel_parent
        self.channel_child.save()

        items_factories.ItemIdeaFactory.create(channel=self.channel_parent)
        items_factories.ConfirmedItemFactory.create(channel=self.channel_parent)

    def test_item_hierarchy_lookup(self):
        """Ensure items can be looked up in hierarchy."""
        items_parent = Item.objects.for_channel(self.channel_parent)
        self.assertIn(self.item_parent, items_parent)
        self.assertIn(self.item_child, items_parent)

    def test_hierarchy_lookup_for_all_managers(self):
        """Looking for items by channel works on every manager."""
        idea_items = Item.idea_objects.for_channel(self.channel_parent)
        self.assertEqual(idea_items.count(), 1)
        confirmed_items = Item.confirmed_objects.for_channel(self.channel_parent)
        self.assertEqual(confirmed_items.count(), 2 + 1)

    def test_item_hierarchy_lookup_with_list_of_channels(self):
        """Ensure items can be looked up in hierarchy."""
        all_channels = Channel.objects.all()
        items_list = Item.objects.for_channels(all_channels)
        self.assertIn(self.item_parent, items_list)
        self.assertIn(self.item_child, items_list)

    def test_items_from_list_of_channels_are_unique(self):
        """Ensure items are not listed twice, from parent and from channel"""
        all_channels = Channel.objects.all()
        items_list = Item.objects.for_channels(all_channels)
        self.assertEqual(items_list.count(), items_list.count())
