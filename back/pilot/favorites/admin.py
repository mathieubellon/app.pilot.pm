from django.contrib import admin

from pilot.favorites.models import Favorite


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'desk', 'target_content_type', 'target_object_id')
    raw_id_fields = ('desk',)
    list_filter = ('desk', )
    ordering = ('desk', )

admin.site.register(Favorite, FavoriteAdmin)

