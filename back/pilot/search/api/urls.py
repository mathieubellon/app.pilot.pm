from django.conf.urls import url

from pilot.search.api import api


urlpatterns = [
    url(
        r'^(?P<type>items|projects)/$',
        api.search,
        name='api_search'
    ),
]
