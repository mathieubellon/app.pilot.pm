
from django.core.exceptions import PermissionDenied
from django.http import QueryDict, HttpRequest
from rest_framework.exceptions import ValidationError

from rest_framework.request import Request

from pilot.desks.utils import connect_to_desk
from pilot.items.api.api import ItemViewSet
from pilot.items.export_item import ItemXLSExporter
from pilot.items.models import Item


def get_items_ids_in_saved_filter(saved_filter):
    """
    We cannot simply directly use ItemFilter to execute the SafedFilter filtering,
    because the ViewSet.filter_queryset() method add additionnal filtering,
    like restricted_editor or ItemViewSet.limit_queryset_in_time.
    We need to simulate an actual request on the ViewSet to get a correct result.

    Thus, the global filtering process is :
        - django_filter.Filter filtering
        - restricted editor filtering
        - additionnal manual filtering in filter_queryset()
    """
    http_request = HttpRequest()
    http_request.method = 'GET'
    # QueryDict expect an encoded query string, not an unicode string
    encoding = 'utf-8'
    query_string = saved_filter.query.encode(encoding)
    http_request.GET = QueryDict(query_string, encoding=encoding)
    drf_request = Request(http_request)
    drf_request.user = saved_filter.user
    drf_request.session = {}
    try:
        connect_to_desk(saved_filter.desk, drf_request)
    except PermissionDenied:
        # This may happen if the saved filter has been created by a deactivated user
        return []

    viewset = ItemViewSet() # For now, only Items are concerned
    viewset.request = drf_request
    viewset.action = 'list'

    try:
        queryset = viewset.filter_queryset(viewset.get_queryset())
    except ValidationError:
        # This may happen if an object referenced by the filter query params does not exists anymore ( deleted/hidden )
        return []

    return list(queryset.values_list('id', flat=True))


def export_saved_filter_to_xls(saved_filter, output_file):
    items_ids = get_items_ids_in_saved_filter(saved_filter)
    items = Item.objects.filter(desk=saved_filter.desk, id__in=items_ids).order_by('id')
    ItemXLSExporter(items, output_file, with_content=True).do_export()
