from django.conf.urls import url

from pilot.channels import views


urlpatterns = [
    # Vue.js ChannelApp pages
    # Don't append trailing slash on views managed by Vue router
    # Don't add a $ at the end of the regex, so we catch all and let the Vue router decide which panel he should open
    url(
        r'^$',
        views.channels_app,
        name='ui_channels_list'
    ),
    url(
        r'^(?P<tab>active|closed)',
        views.channels_app,
        name='ui_channels_list_tab'
    ),
    url(
        r'^(?P<channel_pk>\d+)',
        views.channels_app,
        name='ui_channel_detail'
    ),

    #
    # # Twitter
    # url(
    #     r'^twitter/(?P<credentials_pk>\d+)/$',
    #     views.twitter_credentials_details,
    #     name='ui_twitter_credentials_detail'
    # ),
    # url(
    #     r'^twitter/check/(?P<credentials_pk>\d+)/$',
    #     views.check_token_valid,
    #     name='ui_twitter_check_token_valid'
    # ),
    # url(
    #     r'^twitter/token/(?P<credentials_pk>\d+)/$',
    #     views.create_twitter_token,
    #     name='ui_twitter_token_create'
    # ),
    # url(
    #     r'^twitter/token-verify/(?P<credentials_pk>\d+)/$',
    #     views.verify_token,
    #     name='ui_twitter_token_verify'
    # ),
    # url(
    #     r'^twitter/delete/(?P<credentials_pk>\d+)/$',
    #     views.twitter_credentials_delete,
    #     name='ui_twitter_credentials_delete'
    # ),
    #
    # # Facebook
    # url(
    #     r'^facebook/(?P<credentials_pk>\d+)/$',
    #     views.facebook_credentials_detail,
    #     name='ui_facebook_credentials_detail'
    # ),
    # url(
    #     r'^facebook/delete/(?P<credentials_pk>\d+)/$',
    #     views.facebook_credentials_delete,
    #     name='ui_facebook_credentials_delete'
    # ),
    # url(
    #     r'^facebook/token/(?P<credentials_pk>\d+)/$',
    #     views.create_facebook_token,
    #     name='ui_facebook_token_create'
    # ),
    # url(
    #     r'^facebook/authorize/$',
    #     views.authorize,
    #     name='ui_facebook_authorize'
    # ),
    # url(
    #     r'^facebook/check/(?P<credentials_pk>\d+)/$',
    #     views.check_facebook_token_valid,
    #     name='ui_facebook_check_token_valid'
    # ),
    # url(
    #     r'^facebook/choose_page/(?P<credentials_pk>\d+)/$',
    #     views.choose_page,
    #     name='ui_facebook_choose_page'
    # ),
]
