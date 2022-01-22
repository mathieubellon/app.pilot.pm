from django.conf.urls import url

from pilot.utils.perms.views import organization_admin_template_view

urlpatterns = [
    url(
        r'^subscription/$',
        organization_admin_template_view('main_app.html'),
        name='ui_account_subscription'
    ),
]
