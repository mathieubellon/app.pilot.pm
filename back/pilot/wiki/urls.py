from django.conf.urls import url
from pilot.utils.perms.views import template_view

urlpatterns = [
    url(
        r'^',
        template_view('main_app.html'),
        name='ui_wiki_home_page'
    ),

    url(
        r'^(?P<wiki_page_pk>\d+)',
        template_view('main_app.html'),
        name='ui_wiki_page'
    ),
]
