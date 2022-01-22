import datetime
import factory
import random

from django.utils import timezone

from pilot.desks.tests import factories as desks_factories
from pilot.projects.models import Project
from pilot.utils import states


class ProjectFactory(factory.DjangoModelFactory):
    """Base Project factory."""
    FACTORY_FOR = Project

    state = states.STATE_ACTIVE
    desk = factory.SubFactory(desks_factories.DeskFactory)
    name = factory.LazyAttributeSequence(lambda o, n: "Project{0}-{1}".format(n, o.state))
    description = "Project lorem ipsum dolor sit amet"
    start = timezone.now().date() + datetime.timedelta(days=random.randint(10, 100))  # In UTC.
    end = factory.LazyAttribute(lambda project: project.start + datetime.timedelta(days=10))
    created_by = factory.LazyAttribute(lambda channel: channel.desk.organization.created_by)

    @factory.post_generation
    def targets(self, create, extracted, **kwargs):
        """
        Add optional targets list, e.g.
            - ProjectFactory.create(targets=[target1, target2])
            - project__targets=[target1, target2]
        """
        if extracted:
            # A list of groups were passed in, use them.
            for target in extracted:
                self.targets.add(target)

    @factory.post_generation
    def channels(self, create, extracted, **kwargs):
        """
        Add optional channels list, e.g.
            - ProjectFactory.create(channels=[channel1, channel2])
            - project__channels=[channel1, channel2]
        """
        if extracted:
            for channel in extracted:
                self.channels.add(channel)

    @factory.post_generation
    def owners(self, create, extracted, **kwargs):
        if extracted:
            for user in extracted:
                self.owners.add(user)


class ProjectIdeaFactory(ProjectFactory):
    """Project Idea factory."""

    state = states.STATE_IDEA

