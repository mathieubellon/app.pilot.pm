from django.contrib import admin

from pilot.itemsfilters.models import SavedFilter


class SavedFilterAdmin(admin.ModelAdmin):
    list_display = ('title', 'type','user', 'query',)
    raw_id_fields = ('desk', 'user',)
    search_fields = ('title',)
    list_filter = ('type','desk','user')
    exclude = ('notification_feed_instance_ids', )


admin.site.register(SavedFilter, SavedFilterAdmin)
