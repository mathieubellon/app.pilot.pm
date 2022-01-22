from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from pilot.desks.models import Desk
from pilot.organizations.models import Organization


class UsersInline(admin.TabularInline):
    model = Organization.users.through
    fields = ('user', 'is_organization_admin')
    raw_id_fields = ('user',)
    extra = 1


class DesksInline(admin.TabularInline):
    model = Desk
    fields = ('id', 'name')
    readonly_fields = ('id', 'name')
    extra = 1


class OrganizationAdmin(admin.ModelAdmin):
    inlines = (UsersInline, DesksInline)
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    ordering = ('created_at',)
    raw_id_fields = ('created_by', 'updated_by')
    search_fields = ('name',)

    fieldsets = (
        (None, {'fields': (
            'name',
            'is_active',
            'max_desks',
        )}),
        (_('Abonnement'), {'fields': (
            'stripe_customer_id',
            'stripe_subscription_id',
            'manual_billing',
            'cgv_acceptance_date',
        )}),
        (_('Facturation'), {'fields': (
            'billing_name',
            'billing_address',
            'billing_postal_code',
            'billing_city',
        )}),
        (_('Autre'), {'fields': (
            'created_by',
            'created_at',
            'updated_at',
            'updated_by',
        )}),
    )


admin.site.register(Organization, OrganizationAdmin)
