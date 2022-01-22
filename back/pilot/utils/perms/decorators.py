from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect

"""
Requires the user to have the admin permission ( is_admin )
Redirects to the dashboard and not the login page to avoid an infinite redirect loop
"""
admin_required = user_passes_test(lambda user: user.permissions.is_admin, login_url='/')

"""
Requires the user to have at least the editor permission ( is_editor or is_admin )
Redirects to the dashboard and not the login page to avoid an infinite redirect loop
"""
editor_required = user_passes_test(lambda user: user.permissions.is_editor or user.permissions.is_admin, login_url='/')

"""
Requires the user to be a subscription admin.
Redirects to the dashboard and not the login page to avoid an infinite redirect loop
"""
organization_admin_required = user_passes_test(lambda user: user.permissions.is_organization_admin, login_url='/')


def nologin_required(function=None, name_redirect_to='/'):
    """
    A user must be un-authenticated.

    Usage:
        @nologin_required
    """

    def decorated(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(name_redirect_to)
        return function(request, *args, **kwargs)

    return decorated
