from django.core.exceptions import ValidationError
from django.test import TestCase

from pilot.desks.models import Desk, language_list_validator
from pilot.desks.tests import factories as desks_factories
from pilot.pilot_users.tests import factories as pilot_users_factories



class FactoriesTests(TestCase):
    def test_desk_factory(self):
        """Test DeskFactory."""

        desk = desks_factories.DeskFactory.create()

        self.assertIn(desk.created_by, desk.users.all())
        self.assertEqual(desk.created_by, desk.organization.created_by)
        self.assertIsNotNone(desk.updated_at)
        self.assertEqual(desk.language, 'fr')

        en_desk = desks_factories.DeskFactory.create(language='en')
        self.assertEqual(en_desk.language, 'en')

    def test_desk_factory_with_users(self):
        """Test DeskFactory with additional users."""

        editor = pilot_users_factories.EditorFactory.create()
        restricted_editor = pilot_users_factories.RestrictedEditorFactory.create()
        desk = desks_factories.DeskFactory.create(users=[editor, restricted_editor])

        self.assertIn(desk.created_by, desk.users.all())
        self.assertEqual(3, desk.users.all().count())


class DeskModelTests(TestCase):
    def test_language_list_validator(self):
        language_list_validator(None)  # No error

        with self.assertRaises(ValidationError):
            language_list_validator('fr')

        with self.assertRaises(ValidationError):
            language_list_validator(22)

        with self.assertRaises(ValidationError):
            language_list_validator(['fr'])

        with self.assertRaises(ValidationError):
            language_list_validator(['fr_FR', 'FR'])
        language_list_validator(['fr_FR'])

    def test_desk_language(self):
        desk = desks_factories.DeskFactory()
        pk = desk.pk
        desk.allowed_languages = ['fr_FR', 'en_US']
        desk.save()

        desk = Desk.objects.get(pk=pk)
        self.assertEqual(desk.allowed_languages, ['fr_FR', 'en_US'])
