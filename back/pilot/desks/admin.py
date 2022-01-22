from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from pilot.accounts.usage_limit import UsageLimit
from django.utils.safestring import mark_safe

from pilot.desks.models import Desk
from pilot.utils.url import get_fully_qualified_url

class UsersInline(admin.TabularInline):
    model = Desk.users.through
    fields = ('user', 'impersonate', 'permission',)
    readonly_fields = ('impersonate',)
    raw_id_fields = ('user',)
    extra = 1

    def impersonate(self, obj):
        url = get_fully_qualified_url('/impersonate/{}'.format(obj.user.pk))
        return mark_safe(f'<a href="{url}">Impersonate {obj.user.pk}</a>')


class DeskAdmin(admin.ModelAdmin):
    list_display = ('name', 'subscription_plan', 'organization', 'created_at', 'subscription_terminated')
    list_filter = ('subscription_plan', 'subscription_terminated' )
    exclude = ('users',)
    inlines = (UsersInline,)

    fieldsets = (
        (None, {'fields': (
            'name',
            'is_active',
            'private_items_enabled',
            'creation_forms_fields_visibles_by_default',
            'item_languages_enabled',
            'allowed_languages',
        )}),
        (_('Abonnement'), {'fields': (
            'max_users',
            'max_projects',
            'max_items',
            'max_assets_storage',
            'advanced_features',

            'subscription_plan',
            'display_price',
            'subscription_terminated',
        ),
            'description': "Pour les limites: laisser vide pour conserver les valeurs par défaut de l'abonnement "
                           "ou remplir pour overrider. -1 pour 'Illimité'"
        }),
        (_('Autre'), {'fields': (
            'organization',
            'created_by',
            'created_at',
            'updated_at',
            'updated_by',
        )}),
    )
    readonly_fields = ('subscription_terminated', 'logo')
    ordering = ('created_at',)
    raw_id_fields = ('created_by', 'organization', 'updated_by')
    search_fields = ('name',)

    def save_model(self, request, desk, form, change):
        desk.save()
        UsageLimit.invalidate_max_usage_cache(desk)


admin.site.register(Desk, DeskAdmin)
