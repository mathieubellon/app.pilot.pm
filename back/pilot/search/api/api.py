import logging
import math

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from elasticsearch import exceptions as es_exceptions
from elasticsearch_dsl import Search, Q


logger = logging.getLogger(__name__)

PAGE_SIZE = 10

ITEMS_TYPE = 'items'
PROJECTS_TYPE = 'projects'


def query_elastic_search(type, query, desk, paginate_from=0):
    """
    Handles query to ES and process response.
    Returns response

    :userresquest:string: ES query as a query string query
    :desk:object: A desk object. Search MUST remain within a desk.
        BE REALLY CAREFUL here as content can leak between accounts
    :from:int: In case of pagination from indicates from which results ES must returns a page
        https://www.elastic.co/guide/en/elasticsearch/guide/current/pagination.html

    Returns elasticsearch_dsl Response object
    https://elasticsearch-dsl.readthedocs.org/en/latest/search_dsl.html#response
    """
    if type == ITEMS_TYPE:
        index = settings.ES_ITEM_INDEX
    elif type == PROJECTS_TYPE:
        index = settings.ES_PROJECT_INDEX
    else:
        ValueError("Incorrect search type")

    es_query = Q("query_string", query=query, analyzer="custom_search_analyzer")

    es_search = (
        Search(using=settings.ES_CLIENT, index=index)
        # Search MUST remain within a desk
        .filter("term", desk_id=desk.id)
        .query(es_query)
        .highlight('*')
        .highlight_options(
            require_field_match=False,
            pre_tags=['<b>'],
            post_tags=['</b>']
        )
        .extra(size=PAGE_SIZE)
        .extra(from_=paginate_from)
        # This is useful for debugging, but incurs extra overhead on perf and responses sizes
        # .extra(explain=True)
    )

    # Limit to visible items only
    if type == ITEMS_TYPE:
        es_search = es_search.filter("term", in_trash=False).filter("term", hidden=False)
    if type == PROJECTS_TYPE:
        es_search = es_search.filter("term", hidden=False)

    return es_search.execute()


@api_view(['GET'])
@login_required
def search(request, type):
    """
    Thin wrapper to Elasticsearch
    """
    size = PAGE_SIZE
    query = request.GET.get('query')
    current_page = request.GET.get('page', 1)

    if not query:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Escape FW slash for Elasticsearch not to be confused
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#_reserved_characters
    query = query.replace('/', '\/')

    current_page = max(1, int(current_page))
    paginate_from = (current_page * size) - size

    try:
        es_response = query_elastic_search(
            type,
            query,
            request.desk,
            paginate_from=paginate_from
        )
    except es_exceptions.ConnectionError:
        logger.error("[ElasticSearch Search Error] ConnectionError", exc_info=True)
        return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except es_exceptions.RequestError:
        logger.error("[ElasticSearch Search Error] RequestError", exc_info=True)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if es_response.success():
        total_results = es_response.hits.total.value
        # Compute number of pages for these results
        num_pages = int(math.ceil(total_results / size))

        next_page = (current_page + 1) if current_page < num_pages else None

        return JsonResponse({
            'hits': es_response.to_dict()['hits']['hits'],
            'total_results': total_results,
            'next': next_page,
            'num_pages': num_pages
        })

    else:
        return Response(es_response.e, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
