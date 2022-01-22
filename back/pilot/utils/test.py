import os
import shutil

from django.conf import settings

from pilot.desks.tests import factories as desks_factories
from pilot.item_types.initial_item_types import InitialItemTypeNames
from pilot.pilot_users.tests import factories as pilot_users_factories
from pilot.workflow.initial_states import InitialStateNames


class PilotAdminUserMixin(object):
    def setUp(self):
        """Creates a Pilot user with `admin` privileges with an organization and a desk."""
        super(PilotAdminUserMixin, self).setUp()

        # Create a desk and get its owner.
        self.desk = desks_factories.DeskFactory.create()
        self.user = self.desk.created_by
        self.organization = self.user.organizations.all()[0]

        # Ensure the user is a Pilot admin.
        self.assertTrue(self.user.permissions.is_admin)

        # Log the admin user in.
        self.client.login(email=self.user.email, password='password')


class PilotEditorUserMixin(PilotAdminUserMixin):
    def setUp(self):
        """Creates a Pilot user with `editor` privileges."""
        super(PilotEditorUserMixin, self).setUp()

        self.client.logout()

        self.editor_user = pilot_users_factories.EditorFactory.create(password='password')

        # Ensure the user is a Pilot `restricted editor`.
        self.assertTrue(self.editor_user.permissions.is_editor)

        # Add the `editor` user to the organization.
        self.organization.users.add(self.editor_user)

        # Add the `editor` user to the desk.
        self.desk.users.add(self.editor_user)

        # Log the `editor` user in.
        self.client.login(email=self.editor_user.email, password='password')

        # Ensure that the `editor` is logged in.
        self.assertNotEqual(int(self.client.session['_auth_user_id']), self.user.pk)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.editor_user.pk)


class PilotRestrictedEditorUserMixin(PilotAdminUserMixin):
    def setUp(self):
        """Creates a Pilot user with `restricted editor` privileges."""
        super(PilotRestrictedEditorUserMixin, self).setUp()

        self.client.logout()

        self.restricted_user = pilot_users_factories.RestrictedEditorFactory.create(password='password')

        # Ensure the user is a Pilot `restricted editor`.
        self.assertTrue(self.restricted_user.permissions.is_restricted_editor)

        # Add the `restricted editor` user to the organization.
        self.organization.users.add(self.restricted_user)

        # Add the `restricted editor` user to the desk.
        self.desk.users.add(self.restricted_user)

        # Log the `restricted editor` user in.
        self.client.login(email=self.restricted_user.email, password='password')

        # Ensure that the `restricted editor` is logged in.
        self.assertNotEqual(int(self.client.session['_auth_user_id']), self.user.pk)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.restricted_user.pk)


class WorkflowStateTestingMixin(object):
    def get_workflow_state(self, state_name, desk=None):
        desk = desk or self.desk
        return desk.workflow_states.get(name=state_name)

    def get_state_edition_ready(self, desk=None):
        return self.get_workflow_state(InitialStateNames.EDITION_READY, desk)

    def get_state_validation_ready(self, desk=None):
        return self.get_workflow_state(InitialStateNames.VALIDATION_READY, desk)

    def get_state_publication_ready(self, desk=None):
        return self.get_workflow_state(InitialStateNames.PUBLICATION_READY, desk)

    def get_state_published(self, desk=None):
        return self.get_workflow_state(InitialStateNames.PUBLISHED, desk)

    def get_state_unpublished(self, desk=None):
        return self.get_workflow_state(InitialStateNames.UNPUBLISHED, desk)


class ItemTypeTestingMixin(object):
    def get_item_type(self, item_type_name, desk=None):
        desk = desk or self.desk
        return desk.item_types.get(name=item_type_name)

    def get_item_type_article(self, desk=None):
        return self.get_item_type(InitialItemTypeNames.ARTICLE, desk)

    def get_item_type_twitter(self, desk=None):
        return self.get_item_type(InitialItemTypeNames.TWITTER, desk)

    def get_item_type_facebook(self, desk=None):
        return self.get_item_type(InitialItemTypeNames.FACEBOOK, desk)


class MediaMixin(object):
    """Prevent MEDIA_ROOT pollution with file uploaded in tests"""

    TEST_MEDIA_ROOT = os.path.join(settings.MEDIA_ROOT, '_test')

    def setUp(self):
        """Override MEDIA_ROOT setting"""
        super(MediaMixin, self).setUp()

    def tearDown(self):
        """Restore MEDIA_ROOT setting and remove test media directory"""
        #settings._wrapped = self.wrapped_settings
        super(MediaMixin, self).tearDown()
        assert (self.TEST_MEDIA_ROOT.endswith("_test"))
        shutil.rmtree(self.TEST_MEDIA_ROOT, ignore_errors=True)


# A 500x500 px PNG red square.
PNG_IMG_FILE = "iVBORw0KGgoAAAANSUhEUgAAAfQAAAH0AQMAAADxGE3JAAAAA1BMVEX/AAAZ4gk3AAAANUlEQVR4Ae3BMQEAAADCIPun9lkMYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA5fQAAAWuS3P4AAAAASUVORK5CYII="  # pylint: disable=C0301

# A 20x10 px JPEG green square.
JPEG_IMG_FILE = "/9j/4AAQSkZJRgABAQEASABIAAD//gATQ3JlYXRlZCB3aXRoIEdJTVD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////2wBDAf//////////////////////////////////////////////////////////////////////////////////////wgARCAAKABQDAREAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAAAP/EABUBAQEAAAAAAAAAAAAAAAAAAAAC/9oADAMBAAIQAxAAAAFMgAD/xAAUEAEAAAAAAAAAAAAAAAAAAAAg/9oACAEBAAEFAl//xAAUEQEAAAAAAAAAAAAAAAAAAAAg/9oACAEDAQE/AV//xAAUEQEAAAAAAAAAAAAAAAAAAAAg/9oACAECAQE/AV//xAAUEAEAAAAAAAAAAAAAAAAAAAAg/9oACAEBAAY/Al//xAAUEAEAAAAAAAAAAAAAAAAAAAAg/9oACAEBAAE/IV//2gAMAwEAAgADAAAAEP8A/wD/AP/EABQRAQAAAAAAAAAAAAAAAAAAACD/2gAIAQMBAT8QX//EABQRAQAAAAAAAAAAAAAAAAAAACD/2gAIAQIBAT8QX//EABQQAQAAAAAAAAAAAAAAAAAAACD/2gAIAQEAAT8QX//Z"  # pylint: disable=C0301

TXT_FILE = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque vel dapibus lorem, quis fermentum dui. Aenean venenatis leo at est lobortis, id mollis tortor fermentum."  # pylint: disable=C0301

EMPTY_PROSEMIRROR_DOC = {"content": [{"type": "paragraph"}], "type": "doc"}

def prosemirror_body(string, is_strong=False):
    if not string:
        return EMPTY_PROSEMIRROR_DOC

    if is_strong:
        text_node = {"type":"text", "marks": [{"type": "strong"}], "text": "%s" % string}
    else:
        text_node = {"type":"text","text": "%s" % string}

    return {"type":"doc","content":[{"type":"paragraph","content":[text_node]}]}

def prosemirror_body_string(string):
    return '{"type":"doc","content":[{"type":"paragraph","content":[{"type":"text","text":"%s"}]}]}' % string
