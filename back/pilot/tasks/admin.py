from django.contrib import admin

from pilot.tasks.models import Task
from pilot.utils.forms.fields import NaiveSplitDateTimeField


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'desk', 'item', 'deadline', 'done', 'hidden')
    raw_id_fields = ('desk', 'created_by', 'updated_by', 'assignees', 'done_by', 'item')
    search_fields = ('name', )
    list_filter = ('desk', )
    ordering = ('desk', )

    def get_form(self, request, obj=None, **kwargs):
        kwargs['field_classes'] = {
            'deadline': NaiveSplitDateTimeField
        }
        return super(TaskAdmin, self).get_form(request, obj, **kwargs)


admin.site.register(Task, TaskAdmin)
