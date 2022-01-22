from django.utils.translation import ugettext as _
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404
from django.contrib.auth import logout as auth_logout

from pilot.items.models import EditSession
from pilot.pilot_users.models import UserInOrganization, UserInDesk


class DeskNotFound(Exception):
    pass


def connect_to_desk(desk, request=None, user=None, session=None):
    """
    First, ensure that the connected user has access to the desk and organization.
    Check that the desk and organization are still active.
    Then associate the current request with the desk and organization.
    Set the permissions of the connected user, depending on the desk.
    Set the SESSION_CURRENT_DESK_ID session key to the desk id, to keep the connection on the desk.

    This method may be called aither from the PilotMiddleWare for standard HTTP requests,
    of from a websocket consumer.
    In the latter case, there is no request object, so we need to pass explicitely the user and session.
    """
    if request:
        user = request.user
        session = request.session

    organization = desk.organization

    try:
        user_in_organization = UserInOrganization.objects.get(
            user=user,
            organization=organization
        )
        user_in_desk = UserInDesk.objects.get(
            user=user,
            desk=desk
        )
    except ObjectDoesNotExist:
        raise PermissionDenied(_("Cet utilisateur n'est pas autorisé à se connecter à ce desk"))

    if not organization.is_active:
        auth_logout(request)
        raise PermissionDenied(_("Ce compte est inactif"))

    if not desk.is_active:
        auth_logout(request)
        raise PermissionDenied(_("Ce compte est inactif"))

    user.set_desk_connection(user_in_organization, user_in_desk)

    if request:
        request.organization = desk.organization
        request.desk = desk

    # If the connection is succesful, we must update the session key
    # to continue to connect to this desk in subsequent requests
    session[settings.SESSION_CURRENT_DESK_ID] = desk.id


def get_current_desk(user, session):
    """
    Get the desk where this user is currently connected to
    """
    current_desk_id = session.get(settings.SESSION_CURRENT_DESK_ID)
    if current_desk_id:
        try:
            return user.desks.get(id=current_desk_id)
        except ObjectDoesNotExist:
            # User may have lost access to this desk. We'll fall back on the first desk
            pass

    # Default to returning the first active desk we find
    return user.desks.order_by('pk').filter(is_active=True).first()


def get_desk_for_instance(instance):
    """
    Given an instance of any Model in the application, try to find its desk
    """
    if isinstance(instance, EditSession):
        return instance.item.desk

    # Most models are linked to their Desk through the 'desk' field
    if hasattr(instance, 'desk'):
        return instance.desk

    raise DeskNotFound()


def connect_to_desk_for_instance_or_404(request, instance):
    desk = get_desk_for_instance(instance)

    # The user is already connected to this desk, nothing to do
    if request.desk == desk:
        return

    try:
        connect_to_desk(desk, request)
    except PermissionDenied:
        raise Http404
