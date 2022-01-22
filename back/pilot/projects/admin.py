from django.contrib import admin

from pilot.projects.models import Project


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'end', 'created_by', 'created_at', 'updated_at', 'closed_at',)
    list_filter = ('state', 'desk',)
    raw_id_fields = ('owners', 'created_by', 'updated_by', 'desk', 'channels', 'targets', 'assets', 'category')
    search_fields = ('name',)
    exclude = ('search_vector', 'partial_search_document', 'state')

    def get_queryset(self, request):
        """
        Rewritten method to show all assets.
        """
        qs = self.model.all_the_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

admin.site.register(Project, ProjectAdmin)
