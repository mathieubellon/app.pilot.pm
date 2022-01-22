from django.contrib import admin

from pilot.labels.models import Label


class LabelAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'desk', 'target_type', 'created_at', 'updated_at')
    raw_id_fields = ('desk', 'created_by', 'updated_by')
    search_fields = ('name',)
    list_filter = ('desk', )
    ordering = ('desk', )

admin.site.register(Label, LabelAdmin)
