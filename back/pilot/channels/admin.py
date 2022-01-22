from django.contrib import admin

from pilot.channels.models import Channel


class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'state', 'created_by', 'created_at', 'updated_at', 'closed_at',)
    list_filter = ( 'desk',)
    raw_id_fields = ('created_by', 'updated_by', 'desk', 'owners')
    search_fields = ('name',)

    def get_queryset(self, request):
        """
        Rewritten method to show all assets.
        """
        qs = self.model.all_the_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

admin.site.register(Channel, ChannelAdmin)
