from rest_framework import serializers

from pilot.accounts.models import SubscriptionPlan


class SubscriptionPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubscriptionPlan
        fields = (
            'id',
            'display_price',
            'max_users',
            'max_projects',
            'max_items',
            'max_assets_storage',
            'advanced_features',
            'name'
        )
