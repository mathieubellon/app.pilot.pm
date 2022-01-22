from django.conf.urls import url

from pilot.notifications import views


urlpatterns = [
    url(
        r'^goto/t/(?P<token>\w+)/$',
        views.go_to_notification_target,
        name='notifications_goto'
    ),

    url(
        r'^goto/(?P<notification_id>\d+)/?$',
        views.go_to_notification_target,
        name='notifications_goto_by_id'
    ),

    url(
        r'^inbound/$',
        views.postmark_inbound_webhook,
        name='postmark_inbound_webhook'
    ),

    url(
        r'^bounce/$',
        views.postmark_bounce_webhook,
        name='postmark_bounce_webhook'
    ),

    url(
        r'^settings/(?P<token>\w+)/$',
        views.notifications_settings,
        name='notifications_settings'
    ),
]
