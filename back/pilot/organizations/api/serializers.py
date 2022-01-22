from rest_framework import serializers

from pilot.organizations.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    manual_billing = serializers.ReadOnlyField()

    class Meta:
        model = Organization
        fields = (
            'billing_address',
            'billing_city',
            'billing_name',
            'billing_postal_code',
            'billing_vat',
            'manual_billing',
            'name',
        )
