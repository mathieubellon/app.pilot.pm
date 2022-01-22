from django.contrib import admin, messages

from pilot.queue.models import JobTracker


class JobTrackerAdmin(admin.ModelAdmin):
    list_display = ('job_id', 'job_type', 'state', 'created_at', 'created_by', 'finished_at')
    raw_id_fields = ('desk',)
    list_filter = ('desk', 'state', 'job_type')
    readonly_fields = ('job_id', 'args', 'kwargs', 'timeout')

    actions = ['requeue']

    def requeue(self, request, queryset):
        if queryset.exclude(state__in=(JobTracker.STATE_FAILED, JobTracker.STATE_ZOMBIE)).exists():
            self.message_user(request, "Only failed or zombie jobs can be requed", level=messages.ERROR)
            return

        for job_tracker in queryset:
            job_tracker.requeue()
    requeue.short_description = "Requeue jobs (FAILED or ZOMBIE)"


admin.site.register(JobTracker, JobTrackerAdmin)
