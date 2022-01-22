from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render

from pilot.desks.utils import connect_to_desk_for_instance_or_404
from pilot.items.export_item import ItemContentExporter


# ===== Item App =====
from pilot.items.models import Item


@login_required
def items_app(request, tab='active', item_pk=None, saved_filter_pk=None):
    context = {}

    # For direct access to item detail, from an external source (link in an email) :
    if item_pk:
        item = get_object_or_404(Item.all_the_objects, pk=item_pk)
        connect_to_desk_for_instance_or_404(request, item)

    return render(request, "main_app.html", context)

# ===== Item Export =====


def item_export(request, item_pk):
    # We look for items visible or in trash
    item = get_object_or_404(
        Item.accessible_objects.filter_by_permissions(request.user),
        pk=item_pk,
        desk=request.desk
    )

    session_pk = request.GET.get('session', None)
    export_type = request.GET.get('type', None)

    try:
        item_exporter = ItemContentExporter(item, session_pk)
        return item_exporter.export_to_response(export_type)
    except ValueError as e:
        return HttpResponseBadRequest(e)
