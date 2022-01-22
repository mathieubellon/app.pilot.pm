from collections import OrderedDict
from functools import cached_property

from django.core.paginator import Paginator
from rest_framework import pagination
from rest_framework.response import Response


class PaginatorWithoutAnnotations(Paginator):
    @cached_property
    def count(self):
        """Remove annotations from the COUNT(*) query, that inccurs extra overhead."""
        queryset = self.object_list._chain()
        if queryset.query._annotations:
            queryset.query._annotations = {}
        return queryset.count()


class PilotPageNumberPagination(pagination.PageNumberPagination):
    django_paginator_class = PaginatorWithoutAnnotations

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('num_pages', self.page.paginator.num_pages),
            ('count', self.page.paginator.count),
            ('next', self.page.next_page_number() if self.page.has_next() else None),
            ('previous', self.page.previous_page_number() if self.page.has_previous() else None),
            ('objects', data)
        ]))
