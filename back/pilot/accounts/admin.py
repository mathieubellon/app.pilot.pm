from django.contrib import admin

from pilot.accounts.models import SubscriptionPlan


class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_users', 'max_projects', 'max_items', 'max_assets_storage', 'advanced_features', 'stripe_plan_id')
    list_editable = ('max_users', 'max_projects', 'max_items', 'max_assets_storage', 'advanced_features', 'stripe_plan_id')

admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
