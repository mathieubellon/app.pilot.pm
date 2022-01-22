from django.conf.urls import url

from pilot.big_filter import api

urlpatterns = [

    # Asset List big filter schema
    url(
        r'^schema/assets/list/$',
        api.AssetBigFilterSchema.as_view(),
        name='big_filter_schema_assets_list'
    ),

    # Channel List big filter schema
    url(
        r'^schema/channels/list/$',
        api.ChannelBigFilterSchema.as_view(),
        name='big_filter_schema_channels_list'
    ),

    # Project List big filter schema
    url(
        r'^schema/projects/list/$',
        api.ProjectBigFilterSchema.as_view(),
        name='big_filter_schema_projects_list'
    ),

    # Item List big filter schema
    url(
        r'^schema/items/list/$',
        api.ItemListBigFilterSchema.as_view(),
        name='big_filter_schema_items_list'
    ),

    # Item Calendar big filter schema
    url(
        r'^schema/items/calendar/$',
        api.ItemCalendarBigFilterSchema.as_view(),
        name='big_filter_schema_items_calendar'
    ),
]
