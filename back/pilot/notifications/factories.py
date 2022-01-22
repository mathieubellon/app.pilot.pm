import factory

from pilot.items.tests import factories as items_factories
from pilot.notifications.models import Notification
from pilot.projects.tests import factories as projects_factories
from pilot.pilot_users.tests.factories import PilotUserFactory


class NotificationFactory(factory.DjangoModelFactory):
    """ Base factory for notifications."""
    FACTORY_FOR = Notification
    send_by = factory.SubFactory(PilotUserFactory)
    to = factory.SubFactory(PilotUserFactory)


class OnItemCommentNotificationFactory(NotificationFactory):
    """ Factory for notifications linked to an item. """
    content = factory.Sequence(lambda n: 'Some text %d' % n)
    on = factory.SubFactory(items_factories.ConfirmedItemFactory)
    comment_id = factory.Sequence(lambda n: n)


class OnItemAnnotationNotificationFactory(NotificationFactory):
    """ Factory for notifications linked to an item. """
    content = factory.Sequence(lambda n: 'Some text %d' % n)
    on = factory.SubFactory(items_factories.ConfirmedItemFactory)
    annotation_uuid = factory.Sequence(lambda n: 'uuid-{0}'.format(n)[:36])


class OnItemIdeaNotificationFactory(OnItemCommentNotificationFactory):
    """ Factory for notifications linked to an idea item. """
    on = factory.SubFactory(items_factories.ItemIdeaFactory)


class OnProjectNotificationFactory(NotificationFactory):
    """ Factory for notifications linked to a project. """
    content = factory.Sequence(lambda n: 'Some text %d' % n)
    on = factory.SubFactory(projects_factories.ProjectFactory)
    comment_id = factory.Sequence(lambda n: n)


class OnProjectIdeaNotificationFactory(OnProjectNotificationFactory):
    """ Factory for notifications linked to an idea project. """
    on = factory.SubFactory(projects_factories.ProjectIdeaFactory)
