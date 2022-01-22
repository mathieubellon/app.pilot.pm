from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

from pilot.accounts.api.serializers import SubscriptionPlanSerializer
from pilot.accounts.models import SubscriptionPlan, TRIAL_PLAN_ID
from pilot.accounts.subscription import get_subscription_data, subscribe_desk_to_plan, terminate_desk_subscription, \
    update_stripe_customer_billing_address, update_stripe_customer_card
from pilot.desks.models import Desk
from pilot.desks.utils import connect_to_desk
from pilot.organizations.api.serializers import OrganizationSerializer
from pilot.utils import api as api_utils


class SubscriptionViewset(viewsets.ViewSet):
    permission_classes = [
        api_utils.DeskPermission,
        api_utils.IsOrganizationAdminPermission
    ]

    def retrieve(self, request, *args, **kwargs):
        return Response(get_subscription_data(request.organization))

    @action(detail=True, methods=['POST'])
    def change(self, request, *args, **kwargs):
        desk = get_object_or_404(Desk, id=request.data.get('desk_id'))

        self.set_billing_address_on_organization()

        subscribe_desk_to_plan(
            desk,
            request.user,
            request.data.get('plan_id'),
            request.data.get('token_id')
        )
        # subscribe_desk_to_plan will update desk.organization,
        # but not request.organization
        # We need to keep request.organization up to date with the new data.
        request.organization = desk.organization
        return Response(get_subscription_data(request.organization))

    @action(detail=True, methods=['POST'])
    def deactivate_desk(self, request, *args, **kwargs):
        desk = get_object_or_404(Desk, id=request.data.get('desk_id'))

        # Cannot deactivate the last desk
        if request.organization.desks.filter(is_active=True).count() == 1:
            raise PermissionDenied(_('Impossible de désactiver le dernier desk'))

        desk.is_active = False
        desk.save()

        # The user try to deactivate the desk he is currently connected on,
        # we need to reconnect him to another desk
        if request.desk == desk:
            connect_to_desk(
                desk=request.user.desks.order_by('pk').filter(is_active=True).first(),
                request=request
            )

        return Response(get_subscription_data(request.organization))

    @action(detail=True, methods=['POST'])
    def terminate(self, request, *args, **kwargs):
        desk = get_object_or_404(Desk, id=request.data.get('desk_id'))
        terminate_desk_subscription(desk)
        return Response(get_subscription_data(request.organization))

    @action(detail=True, methods=['PUT'])
    def update_billing_address(self, request, *args, **kwargs):
        self.set_billing_address_on_organization()
        update_stripe_customer_billing_address(request.organization)
        return Response()

    @action(detail=True, methods=['POST'])
    def change_card(self, request, *args, **kwargs):
        update_stripe_customer_card(
            request.organization,
            request.data.get('token_id')
        )
        return Response(get_subscription_data(request.organization))

    def set_billing_address_on_organization(self):
        serializer = OrganizationSerializer(
            self.request.organization,
            data=self.request.data.get('organization'),
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()


class SubscriptionPlanViewSet(ListModelMixin,
                              viewsets.GenericViewSet):
    queryset = SubscriptionPlan.objects.exclude(stripe_plan_id=TRIAL_PLAN_ID)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [
        api_utils.DeskPermission,
        api_utils.IsOrganizationAdminPermission
    ]
