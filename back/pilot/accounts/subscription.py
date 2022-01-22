import logging
from collections import Counter, defaultdict

import stripe
import arrow

from django.conf import settings
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError

from pilot.accounts.models import SubscriptionPlan, TRIAL_PLAN_ID
from pilot.accounts.usage_limit import UsageLimit, get_all_usage_limits, UserUsageLimit
from pilot.organizations.api.serializers import OrganizationSerializer
from pilot.pilot_users.api.serializers import PilotUserLightSerializer

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

CURRENT_VAT_PERCENT = 20.00

def format_amount(amount_in_cents, currency):
    # Amount is expressed in cents, display it in € with decimals
    return "{:.2f}{}".format(amount_in_cents/100., currency)


def format_stripe_amount(stripe_entity, quantity=1, amount_key='amount', currency_key='currency'):
    amount_in_cents = stripe_entity.get(amount_key) * quantity
    currency = stripe_entity.get(currency_key)
    if currency == 'eur':
        currency = '€'
    # Amount is expressed in cents, display it in € with decimals
    return format_amount(amount_in_cents, currency)


def get_stripe_billing_address(organization):
    if '\n' not in organization.billing_address:
        organization.billing_address += '\n'
    line1, line2 = organization.billing_address.split('\n', 1)
    return {
        'name': organization.billing_name,
        'address': {
            'line1': line1,
            'line2': line2,
            'postal_code': organization.billing_postal_code,
            'city': organization.billing_city,
        }
    }


def get_stripe_plans_usage(organization):
    plans_usage = defaultdict(int)

    desks = (organization.desks
             .filter(subscription_terminated=False)
             .exclude(subscription_plan__stripe_plan_id=TRIAL_PLAN_ID) # Don't bill during trial
             .select_related('subscription_plan')
             .annotate(users_count=Count('users')))

    # Order by id to get a consistent ordering
    for desk in desks:
        # We simply count the number of users in each desk.
        plans_usage[desk.subscription_plan.stripe_plan_id] += desk.users_count

    return dict(plans_usage)


def get_stripe_plans_usage_most_expansive_strategy(organization):
    """
    Not currently used, but we may activate this for agencies
    """
    stripe_plans = stripe.Plan.list()
    plans_prices = {plan['id']: plan['amount'] for plan in stripe_plans['data']}
    user_most_expansive_plan = {}

    desks = (organization.desks
             .filter(subscription_terminated=False)
             .exclude(subscription_plan__stripe_plan_id=TRIAL_PLAN_ID) # Don't bill during trial
             .select_related('subscription_plan')
             .prefetch_related('users'))

    for desk in desks:
        for user in desk.users.all():
            current_user_plan = user_most_expansive_plan.get(user.id)
            new_user_plan = desk.subscription_plan.stripe_plan_id

            # Use the new plan when the user has no plan yet,
            # or the current plan is cheaper than the new plan
            if not current_user_plan or plans_prices[current_user_plan] < plans_prices[new_user_plan]:
                user_most_expansive_plan[user.id] = new_user_plan

    return Counter(user_most_expansive_plan.values())


def update_stripe_subscription_items(organization):
    # This organization is not currently subscribed, there's nothing to do
    if not organization.stripe_subscription_id:
        return

    plans_usage = get_stripe_plans_usage(organization)
    subscription_item_to_delete = []
    stripe_subscription_items = stripe.SubscriptionItem.list(subscription=organization.stripe_subscription_id)['data']

    # First update all existing subscription items
    for subscription_item in stripe_subscription_items:
        usage = plans_usage.pop(subscription_item['plan']['id'], None)
        if usage:
            subscription_item.quantity = usage
            subscription_item.prorate = False
            subscription_item.save()
        else:
            subscription_item_to_delete.append(subscription_item)

    # Create subscription items for plan without an existing subscription item
    for plan_id, quantity in plans_usage.items():
        stripe.SubscriptionItem.create(
            subscription=organization.stripe_subscription_id,
            plan=plan_id,
            quantity=quantity,
            prorate=False,
        )

    # Delete subscription items that are not used anymore
    for subscription_item in subscription_item_to_delete:
        subscription_item.delete(prorate=False)


def update_stripe_customer_billing_address(organization):
    if not organization.stripe_customer_id:
        return

    stripe.Customer.modify(
        organization.stripe_customer_id,
        description=organization.billing_name,
        shipping=get_stripe_billing_address(organization),
        business_vat_id=organization.billing_vat
    )


def update_stripe_customer_card(organization, token_id):
    if not organization.stripe_customer_id:
        return

    stripe.Customer.modify(
        organization.stripe_customer_id,
        source=token_id,
    )


def subscribe_desk_to_plan(desk, user, plan_id, token_id):
    organization = desk.organization
    current_plan = desk.subscription_plan
    new_plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    # No changement of plan, nothing to do...
    if current_plan == new_plan and not desk.subscription_terminated:
        raise ValidationError("The new plan is identical to the current plan")

    with transaction.atomic():

        # This organization has not already a stripe customer
        if not organization.stripe_customer_id:
            # There should be a token
            if not token_id:
                raise ValidationError("Token is missing to create a new customer")

            organization.cgv_acceptance_date = timezone.now()

            stripe_customer = stripe.Customer.create(
                email=user.email,
                description=organization.billing_name,
                source=token_id,
                shipping=get_stripe_billing_address(organization),
                business_vat_id=organization.billing_vat
            )
            organization.stripe_customer_id = stripe_customer['id']

        desk.subscription_plan = new_plan
        desk.subscription_terminated = False
        desk.save()

        # This organization has not already a stripe subscription,
        # it's a first subscription
        if not organization.stripe_subscription_id:
            stripe_subscription = stripe.Subscription.create(
                customer=organization.stripe_customer_id,
                items=[{
                    'plan': desk.subscription_plan.stripe_plan_id,
                    'quantity': UserUsageLimit(desk).get_current_usage()
                }],
                tax_percent=CURRENT_VAT_PERCENT,
                prorate=False
            )

            organization.stripe_subscription_id = stripe_subscription['id']

        # This organization already has a running subscription, we need to update it.
        # Recompute each subscription items
        # To have an accurate user count on each desk, for the billed quantities.
        # We also prevent cancelation at period end, because there is at least one subscription
        else:
            update_stripe_subscription_items(organization)

        organization.save()

    UsageLimit.invalidate_max_usage_cache(desk)


def terminate_desk_subscription(desk):
    organization = desk.organization

    # No active stripe subscription : nothing to do
    if not organization.stripe_subscription_id:
        return

    # Keep the customer_id and subscription_id on the organization for future reference,
    # but flag the desk as terminated
    desk.subscription_terminated = True
    desk.save()

    plans_usage = get_stripe_plans_usage(organization)
    # If there's still some billed users in the organization, update the stripe subscription
    if plans_usage:
        update_stripe_subscription_items(organization)

    # If we removed the last subscription item of the organization,
    # Then cancel the stripe subscription
    else:
        stripe_subscription = stripe.Subscription.retrieve(organization.stripe_subscription_id)
        stripe_subscription.delete(at_period_end=True)


def get_desk_subscription_data(desk, organization, is_customer, plans_prices):
    plan = desk.subscription_plan
    trial_period_start = None
    trial_period_end = None
    is_trial = plan.stripe_plan_id == TRIAL_PLAN_ID
    desk_users = desk.users.all()
    billed_users_count = len(desk_users)
    billed_amount = None

    if organization.manual_billing:
        billed_amount_display = desk.display_price
        plan_price = None
    else:
        price_per_user = plans_prices.get(plan.stripe_plan_id, 0)
        billed_amount = billed_users_count * price_per_user
        billed_amount_display = format_amount(billed_amount, '€')
        plan_price = plan.display_price

    # Trial Period
    if is_trial:
        plan_price = _('Gratuit')
        trial_period_start = arrow.get(desk.created_at).isoformat()
        trial_period_end = arrow.get(desk.created_at).shift(days=+30).isoformat()

    is_deactivable = is_trial or desk.subscription_terminated
    return {
        'desk': {
            'id': desk.id,
            'name': desk.name
        },
        'usage_limits': get_all_usage_limits(desk),
        'plan': {
            'id': plan.id,
            'name': plan.name,
            'price': plan_price,
        },
        'is_terminated': desk.subscription_terminated,
        'is_deactivable': is_deactivable,
        'is_running': is_customer and not is_deactivable,
        'trial_period_start': trial_period_start,
        'trial_period_end': trial_period_end,
        'billed_users': PilotUserLightSerializer(desk_users, many=True).data,
        'billed_users_count': billed_users_count,
        'billed_amount': billed_amount,
        'billed_amount_display': billed_amount_display
    }


def get_subscription_data(organization):
    stripe_subcription = {}
    current_period_end = None
    subcription_items = []
    invoices = []
    organization_desks = organization.desks.all().order_by('name')
    is_customer = bool(organization.stripe_customer_id)
    card = None
    plans_prices = {}

    if organization.stripe_subscription_id:
        try:
            stripe_subcription = stripe.Subscription.retrieve(
                organization.stripe_subscription_id,
                expand=['customer', 'customer.default_source']
            )
        except:
            logger.error("[Stripe Error] Could not retrieve subscription (id={})"
                         "".format(organization.stripe_subscription_id),
                         exc_info=True)
        else:
            current_period_end = arrow.get(stripe_subcription.get('current_period_end')).isoformat()

            for stripe_subscription_item in stripe_subcription.get('items', []):
                quantity = stripe_subscription_item['quantity']
                stripe_plan = stripe_subscription_item['plan']
                interval = stripe_plan.get('interval')
                interval_display = _('Mois') if interval == 'month' else _('An')
                amount_display = "{} / {}".format(
                    format_stripe_amount(stripe_plan, quantity=quantity),
                    interval_display
                )
                subcription_items.append({
                    'name': stripe_plan['nickname'],
                    'quantity': quantity,
                    'amount_display': amount_display
                })

    if organization.manual_billing:
        for desk in organization_desks:
            subcription_items.append({
                'name': desk.name,
                'quantity': None,
                'amount_display': desk.display_price
            })

    if is_customer:
        stripe_card = stripe_subcription.get('customer', {}).get('default_source')
        if stripe_card:
            card = {
                'brand': stripe_card['brand'],
                'last4': stripe_card['last4']
            }

        try:
            stripe_invoices = stripe.Invoice.list(customer=organization.stripe_customer_id)
        except:
            logger.error("[Stripe Error] Could not retrieve invoices (customer={})"
                         "".format(organization.stripe_customer_id),
                         exc_info=True)
            invoices = 'error'
        else:
            invoices = [{
                'number': stripe_invoice.get('number'),
                'amount_display': format_stripe_amount(stripe_invoice, amount_key='amount_due'),
                'date': arrow.get(stripe_subcription.get('date')).isoformat(),
                'invoice_pdf': stripe_invoice.get('invoice_pdf'),
                'hosted_invoice_url': stripe_invoice.get('hosted_invoice_url')
            } for stripe_invoice in stripe_invoices.get('data', [])]

        try:
            stripe_plans = stripe.Plan.list()
            plans_prices = {plan['id']: plan['amount'] for plan in stripe_plans['data']}
        except:
            logger.error("[Stripe Error] Could not stripe plans"
                         "".format(organization.stripe_subscription_id),
                         exc_info=True)

    desks = [get_desk_subscription_data(desk, organization, is_customer, plans_prices)
             for desk in organization_desks.filter(is_active=True).prefetch_related('users')]
    inactive_desks = [{
        'id': desk.id,
        'name': desk.name,
        'usage_limits': get_all_usage_limits(desk)
    } for desk in organization_desks.filter(is_active=False)]
    billed_amount = sum((desk['billed_amount'] or 0) for desk in desks)
    return {
        'organization': OrganizationSerializer(organization).data,
        'is_customer': is_customer,
        'desks': desks,
        'inactive_desks': inactive_desks,
        'subcription_items': subcription_items,
        'current_period_end': current_period_end,
        'billed_amount': billed_amount,
        'billed_amount_display': format_amount(billed_amount, '€'),
        'invoices': invoices,
        'card': card,
    }
