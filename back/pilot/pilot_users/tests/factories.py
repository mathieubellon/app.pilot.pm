import factory

from pilot.pilot_users.models import PERMISSION_ADMINS, PERMISSION_EDITORS, PERMISSION_RESTRICTED_EDITORS, PilotUser


class PilotUserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = PilotUser

    username = factory.Sequence("John{0}".format)
    first_name = "John"
    last_name = factory.Sequence("Doe{0}".format)
    email = factory.Sequence("john.doe{0}@example.com".format)

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', 'password')
        user = PilotUser(**kwargs)
        if password is not None:
            user.set_password(password)
        if create:
            user.save()
        return user


class AdminFactory(PilotUserFactory):
    """Creates a user with admin privileges."""
    permission = PERMISSION_ADMINS


class EditorFactory(PilotUserFactory):
    """Creates a user with editor privileges."""
    permission = PERMISSION_EDITORS


class RestrictedEditorFactory(PilotUserFactory):
    """Creates a user with restricted editor privileges."""
    permission = PERMISSION_RESTRICTED_EDITORS
