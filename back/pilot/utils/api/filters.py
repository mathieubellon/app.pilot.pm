from django import forms

import django_filters


class MultipleFilter(django_filters.Filter):
    def __init__(self, **kwargs):
        kwargs['widget'] = forms.SelectMultiple
        kwargs['lookup_expr'] = "in"
        super(MultipleFilter, self).__init__(**kwargs)