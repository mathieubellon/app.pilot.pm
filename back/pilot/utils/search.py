import logging

import django_filters
from django_filters.constants import EMPTY_VALUES

from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchQuery, SearchVectorField, SearchVector
from django.db.migrations.operations.base import Operation
from django.db import models
from django.db.models.expressions import Func, Value
from django.db.models.fields import TextField

from pilot.utils.redis import redis_client

logger = logging.getLogger(__name__)

TS_HEADLINE_OPTIONS = 'StartSel="<span class=\'highlight\'>", StopSel=</span>, MaxFragments=2'

SEARCH_VECTOR_UPDATE_REDIS_KEY = 'pilot:search_vector_update'


class UnaccentFunc(Func):
    function = 'UNACCENT'

    def __init__(self, expression, **extra):
        if not hasattr(expression, 'resolve_expression'):
            expression = Value(expression)
        super(UnaccentFunc, self).__init__(expression, output_field=TextField(), **extra)


class SearchHeadline(Func):
    function = 'ts_headline'
    output_field = TextField()


class CreateSearchDictionary(Operation):
    reversible = True

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if schema_editor.connection.vendor != 'postgresql':
            return
        schema_editor.execute(
            "DROP TEXT SEARCH CONFIGURATION IF EXISTS unaccent;"
            "CREATE TEXT SEARCH CONFIGURATION unaccent ( COPY = simple );"
            "ALTER TEXT SEARCH CONFIGURATION unaccent ALTER MAPPING FOR hword, hword_part, word WITH unaccent, simple;"
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute("DROP TEXT SEARCH CONFIGURATION IF EXISTS unaccent;")

    def describe(self):
        return "Creates extension %s" % self.name


class TrigramIndex(GinIndex):
    """
    A GIN index with the trigram operator.
    """
    def get_sql_create_template_values(self, model, schema_editor, using):
        fields = [model._meta.get_field(field_name) for field_name, order in self.fields_orders]
        tablespace_sql = schema_editor._get_index_tablespace_sql(model, fields)
        quote_name = schema_editor.quote_name
        columns = [
            ('%s %s gin_trgm_ops' % (quote_name(field.column), order)).strip()
            for field, (field_name, order) in zip(fields, self.fields_orders)
        ]
        return {
            'table': quote_name(model._meta.db_table),
            'name': quote_name(self.name),
            'columns': ', '.join(columns),
            'using': using,
            'extra': tablespace_sql,
        }


class FullTextSearchModel(models.Model):
    search_vector = SearchVectorField(null=True)
    partial_search_document = models.TextField(blank=True)

    class Meta:
        abstract = True
        # Indexes doesn't seems to work on abstract classes ?!?
        # Maybe fixed in a later django release
        indexes = [
            # The index for full-text searches
            GinIndex(fields=['search_vector']),
            TrigramIndex(fields=['partial_search_document'])
        ]

    def save(self, *args, **kwargs):
        super(FullTextSearchModel, self).save(*args, **kwargs)

        # Obviously, don't schedule a search vector update if we're currently updating it
        if not getattr(self, 'updating_search_vector', False):
            schedule_search_vector_update(self)

    def update_search_vector(self):
        # We need to force the django ORM to emit an explicit update on the search_vector field,
        # by using update_fields, so Postgres will re-calculate the new tsvector value.
        self.search_vector = self.get_search_vector()
        self.partial_search_document = UnaccentFunc(self.get_search_document())
        self.updating_search_vector = True
        self.prevent_updated_at = True
        super(FullTextSearchModel, self).save(update_fields=['search_vector', 'partial_search_document'])

    def get_search_vector(self):
        search_values = [
            models.Value(value, output_field=models.TextField())
            for value in self.get_search_values()
        ]
        return SearchVector(
            *search_values,
            config='unaccent'
        )

    def get_search_document(self):
        return "\n".join(filter(None, self.get_search_values()))

    def get_search_values(self):
        raise NotImplementedError()


class FreeSearchFilter(django_filters.CharFilter):
    def __init__(self, *args, **kwargs):
        self.highlight_document_field = kwargs.pop('highlight_document_field', 'partial_search_document')
        super(FreeSearchFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        # Always make a full-text search on the search vector
        search_query = SearchQuery(value, config='unaccent')
        query = models.Q(**{self.field_name: search_query})

        # If it's an int, also make an exact id search
        try:
            query = query | models.Q(id=int(value))
        except (TypeError, ValueError):
            pass

        # Add the highlighted snippet
        if self.highlight_document_field:
            qs = qs.annotate(search_headline=SearchHeadline(
                Value('unaccent'),             # name of the fulltext config we use
                self.highlight_document_field, # name of the field holding the search document
                search_query,                  # search query used to generate the highlight
                Value(TS_HEADLINE_OPTIONS),    # The options we use
            ))

        return qs.filter(query)


class PartialMatchFilter(django_filters.CharFilter):
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        return qs.filter(**{self.field_name + '__unaccent__icontains': value})


class SearchFilterSetMixin(django_filters.FilterSet):
    q = FreeSearchFilter(field_name='search_vector', highlight_document_field='partial_search_document')
    q_partial = PartialMatchFilter(field_name='partial_search_document')

    @property
    def qs(self):
        if not hasattr(self, '_qs_search'):
            # Launch the standard filtering
            queryset = super(SearchFilterSetMixin, self).qs

            # If there's a free search term
            # and the full-text search did not return any results,
            # let's try a partial match with the trigram index
            if self.data.get('q') and not queryset.exists():
                self.data._mutable = True
                # Do the search on the partial document, not the full-text one
                self.data['q_partial'] = self.data['q']
                del self.data['q']
                # Reset the cached qs and form properties
                delattr(self, '_qs')
                delattr(self, '_form')

                # Launch the new queryset
                queryset = super(SearchFilterSetMixin, self).qs

            self._qs_search = queryset

        return self._qs_search


def schedule_search_vector_update(instance):
    redis_client.sadd(
        SEARCH_VECTOR_UPDATE_REDIS_KEY,
        f"{ContentType.objects.get_for_model(instance.__class__).id},{instance.id}"
    )


def run_search_vector_update():
    try:
        while True:
            element_to_update = redis_client.spop(SEARCH_VECTOR_UPDATE_REDIS_KEY)

            if element_to_update is None:
                break

            element_to_update = element_to_update.decode()
            content_type_id, instance_id = str(element_to_update).split(',')
            content_type = ContentType.objects.get_for_id(content_type_id)
            instance = content_type.get_object_for_this_type(id=instance_id)
            instance.update_search_vector()
    except:
        logger.error(
            f"Error in run_search_vector_update (element_to_update={element_to_update})",
            exc_info=True
        )
