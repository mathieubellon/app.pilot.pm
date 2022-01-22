from django.contrib import admin

from pilot.workflow.models import WorkflowState


class WorkflowStateAdmin(admin.ModelAdmin):
    list_display = ('label', 'order', 'desk', 'created_at', 'updated_at')
    raw_id_fields = ('desk', 'created_by', 'updated_by')
    search_fields = ('label', 'label')
    list_filter = ('desk', )
    ordering = ('desk', 'order')

admin.site.register(WorkflowState, WorkflowStateAdmin)
