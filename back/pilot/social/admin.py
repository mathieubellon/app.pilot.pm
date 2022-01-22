from django.contrib import admin
from django.utils.translation import ugettext as _

from pilot.social.models import FacebookCredential, TweetLog, TwitterCredential, FacebookLog


class TweetLogAdmin(admin.ModelAdmin):
    list_display = ('item', 'get_channel', 'get_twitter_account', 'tweet_id', 'tweet_dt', 'get_log_status_display')

    def get_channel(self, obj):
        return obj.item.channel

    get_channel.short_description = _("Channel")

    def get_twitter_account(self, obj):
        return obj.item.channel.twittercredential

    get_twitter_account.short_description = _("Twitter Account")

    def get_log_status_display(self, obj):
        """to avoid the get_status_display column header in admin is_display"""
        return obj.get_status_display()

    get_log_status_display.short_description = _("Status")


class FacebookLogAdmin(admin.ModelAdmin):
    list_display = (
        'item',
        'get_channel',
        'get_facebook_account',
        'get_facebook_page_name',
        'status_id',
        'status_dt',
        'get_log_status_display'
    )

    def get_channel(self, obj):
        return obj.item.channel

    get_channel.short_description = _("Channel")

    def get_facebook_account(self, obj):
        return obj.item.channel.facebookcredential

    get_facebook_account.short_description = _("Facebook Account")

    def get_facebook_page_name(self, obj):
        return obj.item.channel.facebookcredential.facebook_page_name

    get_facebook_page_name.short_description = _("Facebook Page")

    def get_log_status_display(self, obj):
        """to avoid the get_status_display column header in admin is_display"""
        return obj.get_status_display()

    get_log_status_display.short_description = _("Status")


class TwitterCredentialsAdmin(admin.ModelAdmin):
    list_display = ('twitter_account', 'channel', 'access_token_key', 'access_token_secret')


class FacebookCredentialsAdmin(admin.ModelAdmin):
    list_display = ('facebook_account', 'channel', 'facebook_page_name')


admin.site.register(TweetLog, TweetLogAdmin)
admin.site.register(FacebookLog, FacebookLogAdmin)
admin.site.register(TwitterCredential, TwitterCredentialsAdmin)
admin.site.register(FacebookCredential, FacebookCredentialsAdmin)
