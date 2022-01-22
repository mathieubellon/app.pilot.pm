import datetime
import copy

from unittest.case import skip

from django.test import TestCase

from pilot.desks.tests import factories as desks_factories
from pilot.items.tests import factories as items_factories
from pilot.item_types import initial_item_types
from pilot.targets.tests import factories as targets_factories
from pilot.projects.tests import factories as projects_factories
from pilot.utils import pilot_languages
from pilot.utils.test import PilotAdminUserMixin, prosemirror_body, WorkflowStateTestingMixin
from pilot.item_types.tests.testing_item_type_definition import ADVANCED_TEST_SCHEMA
from pilot.item_types.tests import factories as item_types_factories


class UtilsTest(PilotAdminUserMixin, TestCase):
    """Test that the language si set accordingly to the visited desk"""

    def setUp(self):
        super(UtilsTest, self).setUp()

    def test_language(self):
        url = '/'
        self.assertEqual(self.desk.language, FR_LANG)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lang="{0}"'.format(FR_LANG))  # Check html lang
        self.assertEqual(response.context['LANGUAGE_CODE'], FR_LANG)

        self.desk.language = pilot_languages.EN_LANG
        self.desk.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lang="{0}"'.format(pilot_languages.EN_LANG))  # Check html lang
        self.assertEqual(response.context['LANGUAGE_CODE'], pilot_languages.EN_LANG)

        self.client.logout()  # For anonymous users Language shoud be FR_LANG
        response = self.client.get(url, follow=True)
        self.assertContains(response, 'lang="{0}"'.format(pilot_languages.FR_LANG))
        self.assertEqual(response.context['LANGUAGE_CODE'], pilot_languages.FR_LANG)


class DiffHistoryTests(WorkflowStateTestingMixin, TestCase):
    """ Test diff history """

    # TODO : migrate tests in this file
    @skip("To be migrated")
    def test_diff_with_custom_type(self):
        desk = desks_factories.DeskFactory.create()
        item_type = item_types_factories.ItemTypeFactory.create(
            desk=desk,
            content_schema=copy.deepcopy(ADVANCED_TEST_SCHEMA)
        )
        item = items_factories.ItemFactory(desk=desk)
        item.save()
        item.item_type = initial_item_types.TWITTER_TYPE
        item.save()

        item.item_type = item_type
        item.save()

        # diff = compare_reversion(item)

        field_names = map(lambda x: x[u'field_name'], diff)
        field_names.sort()
        self.assertEqual([u'Type de contenu'], field_names)
        expected_diff = u'<del style="background:#ffe6e6;">Tweet</del><ins style="background:#e6ffe6;">{}</ins>'.format(item_type.name)

        result = filter(lambda x: x['field_name'] == u'Type de contenu', diff)[0]['field_diff']
        self.assertEqual(expected_diff, result)

    # TODO : migrate tests in this file
    @skip("To be migrated")
    def test_diff_item_type(self):
        item = items_factories.ItemFactory()
        item.save()
        # with reversion.create_revision():
        #item.builtin_item_type = initial_item_types.TWITTER_TYPE
        item.save()

        # with reversion.create_revision():
        #item.builtin_item_type = initial_item_types.FACEBOOK_TYPE
        item.save()


        # diff = compare_reversion(item)

        field_names = map(lambda x: x[u'field_name'], diff)
        field_names.sort()
        self.assertEqual([u'Type de contenu'], field_names)
        expected_diff = u'<del style="background:#ffe6e6;">Tweet</del><ins style="background:#e6ffe6;">Statut Facebook</ins>'
        self.assertEqual(expected_diff, diff[0]['field_diff'])

    # TODO : migrate tests in this file
    @skip("To be migrated")
    def test_diff_history_generic(self):
        self.maxDiff = None
        item = items_factories.ItemFactory()
        old_target = targets_factories.TargetFactory(name="old_target")
        new_target = targets_factories.TargetFactory(name="new_target")
        old_project = projects_factories.ProjectFactory(name="old_project")
        new_project = projects_factories.ProjectFactory(name="new_project")

        # with reversion.create_revision():
        item.project = old_project
        item.targets = [old_target]
        item.workflow_state = self.get_state_edition_ready(item.desk)
        item.guidelines = "old_guidelines"
        item.publication_dt = datetime.datetime(2016, 3, 1)
        item.json_content['body'] = prosemirror_body('old')
        item.state_dates = {'published': '2016-03-18'}
        item.save()

        # with reversion.create_revision():
        item.project = new_project
        item.targets = [new_target]
        item.workflow_state = self.get_state_publication_ready(item.desk)
        item.guidelines = "new_guidelines"
        item.publication_dt = datetime.datetime(2016, 3, 2)
        item.json_content['body'] = prosemirror_body('new')
        item.state_dates = {'published': '2016-03-19'}
        item.save()

        # diff = compare_reversion(item)

        field_names = map(lambda x: x[u'field_name'], diff)
        field_names.sort()


        self.assertEqual([u'Contenu', u'Dates des \xe9tats', u'Quoi et Qui', u'\xc9tat de workflow'], field_names)

        expected_diff = {u'Contenu': True,
                         u'Dates des \xe9tats': u'<ul><li>En ligne : <del>1 mars 2016</del> -> <ins>2 mars 2016</ins></li></ul>',
                         u'Quoi et Qui': u'<del style="background:#ffe6e6;">old</del><ins style="background:#e6ffe6;">new</ins><span>_guidelines</span>',
                         u'\xc9tat de workflow': u'<del>Brouillon</del> -> <ins>A publier</ins>'
                         }

        for field_name in field_names:
            result = filter(lambda x: x['field_name'] == field_name, diff)[0]['field_diff']
            self.assertEqual(expected_diff[field_name], result)
