from django.contrib import admin

from pilot.activity_stream.models import Activity


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('actor', 'actor_email', 'verb', 'target', 'target_str', 'action_object',  'action_object_str', 'created_at')


admin.site.register(Activity, ActivityAdmin)
