from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.views.generic.base import TemplateView

from pilot.items.api.filters import ItemFilter
from pilot.utils.perms import admin_required
from pilot.utils.perms.decorators import organization_admin_required


def filter_items_for_sharing(items_queryset, sharing):
    """
    Keep only items in the queryset that are part of the sharing
    """
    item_filter = ItemFilter(
        data=QueryDict(sharing.get_query_string()),
        queryset=items_queryset
    )

    # qs is the filtered queryset, so only the items that belongs to the sharing will be there
    return item_filter.qs


def template_view(template_name):
    return login_required(
        TemplateView.as_view(template_name=template_name)
    )


def admin_template_view(template_name):
    return login_required(
        admin_required(
            TemplateView.as_view(template_name=template_name)
        )
    )


def organization_admin_template_view(template_name):
    return login_required(
        organization_admin_required(
            TemplateView.as_view(template_name=template_name)
        )
    )
