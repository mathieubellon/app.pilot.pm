from pilot.desks.models import Desk
from pilot.pilot_users.tests import factories as pilot_users_factories


def user_list():
    desk = Desk.objects.first()

    # Create only 9 active users to reach 10, because there's already  the base user
    users = pilot_users_factories.PilotUserFactory.create_batch(9, is_active=True)
    users += pilot_users_factories.PilotUserFactory.create_batch(5, is_active=False)

    desk.organization.users.add(*users)
    desk.users.add(*users)
