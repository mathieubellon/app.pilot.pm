import datetime

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.test import TestCase
from django.utils import timezone

from pilot.projects.tests import factories as projects_factories
from pilot.desks.tests import factories as desks_factories
from pilot.utils import states


class FactoriesTests(TestCase):
    def test_project_factory(self):
        """Test ProjectFactory."""
        project = projects_factories.ProjectFactory.create()
        self.assertIsNotNone(project.desk)
        self.assertIsNone(project.closed_at)
        self.assertEqual(project.owners.count(), 0)
        self.assertEqual(project.created_by, project.desk.organization.created_by)
        self.assertEqual(project.state, states.STATE_ACTIVE)
        self.assertEqual(project.created_by_external_email, '')

        # Still no assertNoException() method
        try:
            project.get_absolute_url()
        except Exception as e:
            self.fail("Error on project.get_absolute_url(): {0}".format(e))

    def test_project_idea_factory(self):
        """Test ProjectIdeaFactory."""
        project = projects_factories.ProjectIdeaFactory.create()
        self.assertEqual(project.state, states.STATE_IDEA)

    def test_editable_project_idea_factory(self):
        """Test ProjectIdeaFactory."""
        project = projects_factories.EditablePublicProjectFactory.create()
        self.assertEqual(project.state, states.STATE_IDEA)


class ProjectModelTests(TestCase):
    def tearDown(self):
        # Delete all Project objects after each test.
        Project.objects.all().delete()

    def test_start_gt_end(self):
        """Create a Project whith a start greater than the end."""
        with self.assertRaises(ValidationError):
            projects_factories.ProjectFactory.create(
                start=timezone.now(), end=timezone.now() - datetime.timedelta(days=10))

    def test_active_and_closed_managers(self):
        """Test ActiveProjectManager and ClosedProjectManager."""
        TOTAL_PROJECTS = 6

        projects = projects_factories.ProjectFactory.create_batch(
            size=TOTAL_PROJECTS, state=states.STATE_ACTIVE)

        # Close the latter half of projects.
        for project in projects[TOTAL_PROJECTS / 2:]:
            project.close()

        self.assertEqual(Project.objects.all().count(), TOTAL_PROJECTS)
        self.assertEqual(Project.active_objects.all().count(), TOTAL_PROJECTS / 2)
        self.assertEqual(Project.closed_objects.all().count(), TOTAL_PROJECTS / 2)

    def test_idea_project_manager(self):
        """Test IdeaProjectManager."""
        projects_factories.ProjectFactory.create()
        projects_factories.ProjectIdeaFactory.create()
        self.assertEqual(Project.objects.all().count(), 2)
        self.assertEqual(Project.idea_objects.all().count(), 1)

    def test_unconfirmed_project_manager(self):
        """Test UnconfirmedProjectManager."""

        projects_factories.ProjectFactory.create()
        self.assertEqual(Project.unconfirmed_objects.all().count(), 0)

        projects_factories.ProjectIdeaFactory.create()
        self.assertEqual(Project.unconfirmed_objects.all().count(), 1)

        projects_factories.ProjectFactory.create(state=states.STATE_REJECTED)
        self.assertEqual(Project.unconfirmed_objects.all().count(), 2)

    def test_confirmed_project_manager(self):
        """Test ConfirmedProjectManager."""

        desk = desks_factories.DeskFactory.create()

        # Create 1 Item for each existing ProjectWorkflow.
        for s in ProjectWorkflow.states:
            projects_factories.ProjectFactory.create(state=s.name, desk=desk)

        # Ensure 1 object has been created for each existing WorkflowState
        self.assertEqual(
            len(set(Project.objects.all().values_list('state', flat=True))),
            len(ProjectWorkflow.states)
        )

        # The default manager must returns all projects.
        self.assertEqual(
            Project.objects.all().count(),
            len(ProjectWorkflow.states)
        )
        states = Project.objects.all().values_list('state', flat=True)
        self.assertIn(states.STATE_IDEA, states)
        self.assertIn(states.STATE_REJECTED, states)
        self.assertIn(states.STATE_ACTIVE, states)
        self.assertIn(states.STATE_CLOSED, states)

        # The confirmed_objects manager should returns all projects except the `idea` and `rejected` status.
        self.assertEqual(
            Project.confirmed_objects.all().count(),
            len(ProjectWorkflow.states) - 2
        )
        confirmed_states = Project.confirmed_objects.all().values_list('state', flat=True)
        self.assertNotIn(states.STATE_IDEA, confirmed_states)
        self.assertNotIn(states.STATE_REJECTED, confirmed_states)
        self.assertIn(states.STATE_ACTIVE, confirmed_states)
        self.assertIn(states.STATE_CLOSED, confirmed_states)

        # The confirmed_objects manager should returns all projects except the  `rejected` status.
        self.assertEqual(
            Project.objects.ideas_and_active().count(),
            len(ProjectWorkflow.states) - 1
        )
        ideas_and_active_states = Project.objects.ideas_and_active().values_list('state', flat=True)
        self.assertIn(states.STATE_IDEA, ideas_and_active_states)
        self.assertNotIn(states.STATE_REJECTED, ideas_and_active_states)
        self.assertIn(states.STATE_ACTIVE, ideas_and_active_states)
        self.assertIn(states.STATE_CLOSED, ideas_and_active_states)


class ProjectWorkflowTests(TestCase):
    """Test Project workflow."""

    def test_close(self):
        """Create an active Project then close it."""

        project = projects_factories.ProjectFactory.create(state=states.STATE_ACTIVE)
        self.assertEqual(project.state, states.STATE_ACTIVE)
        self.assertIsNone(project.closed_at)

        # Close the project.
        project.close(user=project.created_by)
        self.assertEqual(project.state, states.STATE_CLOSED)
        self.assertIsNotNone(project.closed_at)
        self.assertEqual(project.updated_by, project.created_by)


class ProjectTagsTests(TestCase):
    """Test Project tags."""

    def test_tags(self):
        desk1 = desks_factories.DeskFactory.create()
        project1 = projects_factories.ProjectFactory.create(desk=desk1)
        project1.tags.add('tag1')
        self.assertEqual(1, project1.tags.all().count())

        desk2 = desks_factories.DeskFactory.create()
        project2 = projects_factories.ProjectFactory.create(desk=desk2)
        project2.tags.add('tag1')
        project2.tags.add('tag2')
        self.assertEqual(2, project2.tags.all().count())

        self.assertEqual(1, desk1.projects.filter(tags__name__in=['tag1']).count())
        self.assertEqual(1, desk2.projects.filter(tags__name__in=['tag1']).count())

        # All tags on all projects.
        self.assertEqual(2, Project.objects.filter(tags__name__in=['tag1']).count())

        # Get all tags on a specific desk.
        self.assertEqual(1, Tag.objects.filter(Q(item__desk=desk1) | Q(project__desk=desk1)).distinct().count())
