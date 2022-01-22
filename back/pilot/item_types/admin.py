import json

from django.contrib import admin

from pilot.item_types.models import ItemType, ItemTypeSnapshot


class ItemTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'desk')
    raw_id_fields = ('desk', 'updated_by', 'created_by')


admin.site.register(ItemType, ItemTypeAdmin)


class ItemTypeSnapshotAdmin(admin.ModelAdmin):
    list_display = ('item_type', 'item_type_id', 'desk', 'created_at', 'created_by',)
    list_filter = ('item_type__desk',)
    search_fields = ('item_type__name', 'item_type__id')
    exclude = ('serialized_data',)
    readonly_fields = ('item_type', 'created_at', 'created_by', 'get_serialized_data',)


    def desk(self, snapshot):
        return snapshot.item_type.desk
    desk.short_description = 'Desk'

    def get_serialized_data(self, snapshot):
        return json.dumps(snapshot.serialized_data)
    get_serialized_data.short_description = 'Content schema'


admin.site.register(ItemTypeSnapshot, ItemTypeSnapshotAdmin)
