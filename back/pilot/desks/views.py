from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect

from pilot.desks.models import Desk
from pilot.desks.utils import connect_to_desk
from pilot.main.menu import MENU_ELEMENTS_DICT
from pilot.utils import perms as perms_utils


@login_required
@perms_utils.admin_required
def desk_admin(request):
    """Desk edit."""
    return render(request, "main_app.html")


@login_required
def desk_switch(request):
    """ Switch from desk to desk inside an organization """
    try:
        desk = Desk.objects.get(id=int(request.POST.get('desk_id')))
    except:
        # desk_id is either absent, or not an integer, or there's no corresponding Desk.
        # This is a bad request
        return HttpResponseBadRequest()

    try:
        connect_to_desk(desk, request)
    except PermissionDenied as e:
        # The user does not have access to the desk
        return HttpResponseForbidden(str(e))

    return redirect(MENU_ELEMENTS_DICT[request.user.login_menu].home_view)
