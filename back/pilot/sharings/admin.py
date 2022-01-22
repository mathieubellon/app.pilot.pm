from django.contrib import admin

from pilot.sharings.models import Sharing, ItemFeedback


class SharingAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'desk',
        'type',
        'is_editable',
        'deactivated',
    )
    raw_id_fields = ('desk', 'created_by', 'item', 'project', 'channel', 'saved_filter')
    readonly_fields = ('token',)


class ItemFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        'sharing',
        'desk',
        'item',
        'status',
        'created_at'
    )
    raw_id_fields = ('desk', 'sharing', 'item')


admin.site.register(Sharing, SharingAdmin)
admin.site.register(ItemFeedback, ItemFeedbackAdmin)
