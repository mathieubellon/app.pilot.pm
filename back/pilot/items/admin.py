from django.contrib import admin


# class ItemAdminForm(ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(ItemAdminForm, self).__init__(*args, **kwargs)
#         queryset = Label.objects.filter(
#             target_type=LabelTargetType.ITEM_TAGS
#         )
#         if self.instance.desk:
#             queryset = queryset.filter(desk=self.instance.desk)
#         self.fields['tags'].queryset = queryset
from pilot.items.models import EditSession, Item, ItemStats


class EditSessionInline(admin.TabularInline):
    model = EditSession
    extra = 0
    fields = ('version', 'restored_from', 'created_by', 'created_at',)
    readonly_fields = fields
    show_change_link = True


class ItemAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'id',
        'desk',
        'title',
        'workflow_state',
        'in_trash',
        'hidden',
        'item_type',
        'created_by',
        'publication_dt',
    )
    list_filter = ('desk', 'item_type', 'created_by',)
    search_fields = (
        'id',
        'workflow_state__label',
        'item_type__name',
    )
    ordering = ['-updated_at']
    exclude = ('search_vector', 'partial_search_document')
    raw_id_fields = (
        'copied_from',
        'created_by',
        'updated_by',
        'desk',
        'channels',
        'tags',
        'targets',
        'master_translation',
        'project',
        'assets',
        'owners',
        'item_type'
    )
    inlines = [
        EditSessionInline,
    ]
    # form = ItemAdminForm

    def get_queryset(self, request):
        """
        Rewritten method to show all items.
        """
        qs = self.model.all_the_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class EditSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'item_id',  'version', 'created_by', 'created_at',)
    raw_id_fields = ('item', 'restored_from', 'created_by',)
    search_fields = ('json_content',)
    date_hierarchy = 'created_at'


class ItemStatsAdmin(admin.ModelAdmin):
    list_display = ('desk', 'items_created_num',)
    raw_id_fields = ('desk',)


admin.site.register(Item, ItemAdmin)
admin.site.register(EditSession, EditSessionAdmin)
admin.site.register(ItemStats, ItemStatsAdmin)
