from django.conf.urls import url

from pilot.pilot_users import views
from pilot.utils.perms.views import admin_template_view
from pilot.utils import perms as perms_utils


urlpatterns = [

    # -----------
    # Auth Vue.js app
    # -----------

    url(
        r'^login/$',
        perms_utils.nologin_required(views.auth_app),
        name='auth_login'
    ),
    url(
        r'^registration/$',
        perms_utils.nologin_required(views.auth_app),
        name='auth_registration'
    ),

    ########################################
    # /!\ BIG FAT WARNING
    # The order of the two following routes is CRITICAL.
    # If you invert them, the .* in the second route will catch all and the first will never get called !!
    ########################################
    url(
        r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        views.PilotPasswordResetConfirmView.as_view(),
        name='auth_password_reset_confirm'
    ),
    url(
        r'^password/reset/.*$',
        views.auth_app,
        name='auth_password_reset'
    ),

    url(
        r'^registration/confirm/email/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        views.registration_confirm,
        name='ui_registration_confirm'
    ),
    url(
        r'^users/confirm/(?P<token>\w+)/$',
        views.auth_app,
        name='ui_invitation_confirm'
    ),

    # -----------
    # Logout
    # -----------

    url(
        r'^logout/$',
        views.PilotLogoutView.as_view(),
        name='auth_logout'
    ),

    # -----------
    # User Admin Vue.js app
    # -----------

    # User list Vue.js app, which need a catch-all regex for the Vue-router
    url(
        r'^users/.*$',
        admin_template_view('main_app.html'),
        name='ui_users_list'
    ),
]
