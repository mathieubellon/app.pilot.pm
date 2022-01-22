from django.conf.urls import url

from pilot.desks import views


urlpatterns = [

    url(r'^switch/$', views.desk_switch, name='ui_desk_switch'),

    # -----------
    # Desk Admin Vue.js app
    # -----------

    url(r'^$', views.desk_admin, name='ui_desk'),
    url(r'^edit', views.desk_admin, name='ui_desk_edit'),
    url(r'^config', views.desk_admin, name='ui_desk_config'),
    url(r'^export', views.desk_admin, name='ui_desk_export'),
]
