from django.contrib import admin

from pilot.wiki.models import WikiPage


class WikiPageAdmin(admin.ModelAdmin):
    list_display = ('name',  'desk',  'created_at', 'updated_at')
    raw_id_fields = ('desk', 'created_by', 'updated_by')
    search_fields = ('name',)
    list_filter = ('desk', )
    ordering = ('desk', 'name')


admin.site.register(WikiPage, WikiPageAdmin)
