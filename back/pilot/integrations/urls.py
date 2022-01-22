from django.conf.urls import url
from pilot.utils.perms.views import admin_template_view

urlpatterns = [
    url(
        r'^tokens/$',
        admin_template_view('main_app.html'),
        name='integrations_tokens_admin'
    ),
]
