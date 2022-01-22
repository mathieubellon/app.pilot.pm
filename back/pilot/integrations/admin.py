from django.contrib import admin

from pilot.integrations.models import ApiToken


class ApiTokenAdmin(admin.ModelAdmin):
    list_display = ('desk', 'created_at', 'token',)
    raw_id_fields = ('desk',)
    readonly_fields = ('token',)


admin.site.register(ApiToken, ApiTokenAdmin)
