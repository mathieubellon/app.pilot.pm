from django.contrib import admin

from pilot.targets.models import Target


class TargetAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    raw_id_fields = ('desk', 'created_by', 'updated_by')
    search_fields = ('name',)


admin.site.register(Target, TargetAdmin)
