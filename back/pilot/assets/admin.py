from django.contrib import admin

from pilot.assets.models import Asset, AssetRight


class AssetAdmin(admin.ModelAdmin):
    list_display = ('title', 'file', 'size','in_media_library','created_at','updated_at','item_linked')
    raw_id_fields = ('desk', 'updated_by', 'created_by')
    list_filter = ('desk',)
    list_editable = ('in_media_library',)
    ordering = ('-created_at',)
    search_fields = ('title', 'file', 'url', 'size','items__id',)
    readonly_fields = ('file',)
    exclude = ('search_vector', 'partial_search_document')
    list_per_page = 400

    def item_linked(self, instance):
        return ','.join([str(i) for i in instance.items.all()])

    def get_queryset(self, request):
        """
        Rewritten method to show all assets.
        """
        qs = self.model.all_the_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class AssetRightAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'desk', 'asset','medium','expiry')
    readonly_fields = ('desk', 'updated_by', 'created_by', 'asset', 'medium')


admin.site.register(Asset, AssetAdmin)
admin.site.register(AssetRight, AssetRightAdmin)
