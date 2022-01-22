from django.contrib import admin

from pilot.notifications.models import Notification, NotificationFeed


def make_read(modeladmin, request, queryset):
    for i in queryset:
        if i.is_read:
            pass
        else:
            i.is_read = 'False'
            i.save()


make_read.short_description = "Mark selected notification as read"


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('send_by', 'to', 'send_at', 'is_read', 'linked_object')
    list_filter = ('to', 'is_read',)
    raw_id_fields = ('send_by', 'to')
    actions = [make_read]


class NotificationFeedAdmin(admin.ModelAdmin):
    list_display = ('saved_filter', 'feed_type', 'desk', 'user',  'send_email')
    raw_id_fields = ('desk', 'user', 'saved_filter')


admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationFeed, NotificationFeedAdmin)
