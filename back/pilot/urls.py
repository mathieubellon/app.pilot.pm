from django.conf import settings
from django.urls import path, re_path, include
from django.contrib import admin
from django.views.generic.base import RedirectView

from pilot.accounts.api.urls import account_api_router
from pilot.accounts.api.urls import plans_api_router
from pilot.activity_stream.api.urls import activity_stream_api_router
from pilot.assets.api.urls import assets_api_router
from pilot.channels.api.urls import channels_api_router
from pilot.desks.api.urls import desks_api_router, export_api_router
from pilot.favorites.api.urls import favorites_api_router
from pilot.integrations.api.urls import integrations_api_router
from pilot.integrations.public_endpoints.urls import integrations_endpoints_router_beta
from pilot.item_types.api.urls import item_types_api_router
from pilot.items.api.urls import items_api_router, items_api_router_shared
from pilot.itemsfilters.api.urls import item_filters_api_router
from pilot.labels.api.urls import labels_api_router
from pilot.list_config.api.urls import list_config_api_router, list_config_api_router_shared
from pilot.notifications.api.urls import notifications_api_router
from pilot.pilot_users.api.urls import users_api_router, users_me_api_router
from pilot.projects.api.urls import projects_api_router, urlpatterns_shared_project
from pilot.sharings.api.urls import sharings_api_router, sharings_api_router_shared, urlpatterns_shared_item
from pilot.targets.api.urls import targets_api_router
from pilot.tasks.api.urls import tasks_api_router
from pilot.wiki.api.urls import wiki_api_router
from pilot.workflow.api.urls import workflow_api_router

urlpatterns = [

    # Admin
    path('cockpit/', admin.site.urls),

    # API
    path('api_auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/big_filter/', include('pilot.big_filter.urls')),
    path('api/items/', include('pilot.items.api.urls')),
    path('api/projects/', include('pilot.projects.api.urls')),
    path('api/search/', include('pilot.search.api.urls')),

    path('api/', include(
        account_api_router.urls +
        activity_stream_api_router.urls +
        assets_api_router.urls +
        channels_api_router.urls +
        desks_api_router.urls +
        export_api_router.urls +
        favorites_api_router.urls +
        integrations_api_router.urls +
        item_types_api_router.urls +
        items_api_router.urls +
        item_filters_api_router.urls +
        labels_api_router.urls +
        list_config_api_router.urls +
        notifications_api_router.urls +
        plans_api_router.urls +
        projects_api_router.urls +
        sharings_api_router.urls +
        targets_api_router.urls +
        tasks_api_router.urls +
        users_me_api_router.urls +
        users_api_router.urls +
        wiki_api_router.urls +
        workflow_api_router.urls
    )),

    # Shared API
    re_path(r'^api/shared/(?P<token>\w+)/', include(
        urlpatterns_shared_project +
        urlpatterns_shared_item +
        items_api_router_shared.urls +
        sharings_api_router_shared.urls +
        list_config_api_router_shared.urls
    )),

    # Integrations
    path('integrations/beta/', include(integrations_endpoints_router_beta.urls)),

    # Django-impersonate
    path('impersonate/', include('impersonate.urls')),

    # UI
    path('', include('pilot.main.urls')),
    path('', include('pilot.pilot_users.urls')),
    path('', include('pilot.pilot_users.api.urls')),
    path('', include('pilot.dashboard.urls')),
    path('', include('pilot.accounts.urls')),
    path('assets/', include('pilot.assets.urls')),
    path('channels/', include('pilot.channels.urls')),
    path('desk/', include('pilot.desks.urls')),
    path('integrations/', include('pilot.integrations.urls')),
    path('items/types/', include('pilot.item_types.urls')),
    path('items/', include('pilot.items.urls')),
    path('labels/', include('pilot.labels.urls')),
    path('notifications/', include('pilot.notifications.urls')),
    path('projects/', include('pilot.projects.urls')),
    path('sharings/', include('pilot.sharings.urls')),
    path('targets/', include('pilot.targets.urls')),
    path('tasks/', include('pilot.tasks.urls')),
    path('wiki/', include('pilot.wiki.urls')),
    path('workflow/', include('pilot.workflow.urls')),

    # Use set_language view to toggle (fr/en) language for anonymous users
    path('i18n/', include('django.conf.urls.i18n')),

    # Redirect, just in case someone click on an old url in the wild
    re_path(r'^mydashboard$', RedirectView.as_view(url='/dashboard')),
    re_path(r'^asset/(?P<tail>.*)$', RedirectView.as_view(url='/assets/%(tail)s', query_string=True)),
    re_path(r'^channel/(?P<tail>.*)$', RedirectView.as_view(url='/channels/%(tail)s', query_string=True)),
    re_path(r'^item/(?P<tail>.*)$', RedirectView.as_view(url='/items/%(tail)s', query_string=True)),
    re_path(r'^label/(?P<tail>.*)$', RedirectView.as_view(url='/labels/%(tail)s', query_string=True)),
    re_path(r'^project/(?P<tail>.*)$', RedirectView.as_view(url='/projects/%(tail)s', query_string=True)),
    re_path(r'^target/(?P<tail>.*)$', RedirectView.as_view(url='/targets/%(tail)s', query_string=True)),

    # Sharings redirects
    re_path(
        r'^custom/shared/(?P<shared_filter_pk>\d+)/(?P<token>\w+)/$',
        RedirectView.as_view(url='/sharings/%(token)s', query_string=True)
    ),
    re_path(
        r'^custom/shared/(?P<item_pk>\d+)/(?P<shared_filter_pk>\d+)/(?P<token>\w+)/$',
        RedirectView.as_view(url='/sharings/%(token)s', query_string=True)
    ),
    re_path(
        r'^custom/shared/password/(?P<shared_filter_pk>\d+)/(?P<token>\w+)/$',
        RedirectView.as_view(url='/sharings/password/%(token)s', query_string=True)
    ),

    re_path(
        r'^items/sharings/(?P<sharing_pk>\d+)/(?P<token>\w+)/(?P<step>step1Content|step2Validation)?$',
        RedirectView.as_view(url='/sharings/%(token)s', query_string=True)
    ),
    re_path(
        r'^items/sharings/password/(?P<sharing_pk>\d+)/(?P<token>\w+)/$',
        RedirectView.as_view(url='/sharings/password/%(token)s', query_string=True)
    )
]


if settings.DEBUG:
    import django.views.static
    from django.conf.urls import url
    import debug_toolbar
    from doc.open_api import internal_api_schema_view

    urlpatterns += [
        # Static file serving
        re_path(r'^media/(?P<path>.*)$', django.views.static.serve, kwargs={'document_root': settings.MEDIA_ROOT, }),
        # Debug toolbar
        path('__debug__/', include(debug_toolbar.urls)),
        # Swagger documentation for our backend API,
        url(r'^api/swagger(?P<format>\.json|\.yaml)$', internal_api_schema_view.without_ui(cache_timeout=0), name='schema-json'),
        url(r'^api/swagger/$', internal_api_schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        url(r'^api/redoc/$', internal_api_schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]

# Don't use whitenoise to serve statics in testing, because it requires to collectstatic each time.
# Use django serve view instead.
if settings.TESTING:
    from django.contrib.staticfiles.views import serve as serve_statics

    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve_statics, kwargs={'insecure': True}),
    ]
