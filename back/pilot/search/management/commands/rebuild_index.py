import logging
import sys

from elasticsearch.client.indices import IndicesClient

from django.core.management.base import BaseCommand
from django.conf import settings

from pilot.projects.models import Project
from pilot.items.models import Item
from pilot.search.api.serializers import ItemSearchDocTypeSerializer, ProjectSearchDocTypeSerializer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, verbosity=2, **kwargs):
        logger.info(f"[Command Start] {' '.join(sys.argv[1:])}")

        indicies_client = IndicesClient(settings.ES_CLIENT)
        if indicies_client.exists(settings.ES_ITEM_INDEX):
            indicies_client.delete(settings.ES_ITEM_INDEX)
        if indicies_client.exists(settings.ES_PROJECT_INDEX):
            indicies_client.delete(settings.ES_PROJECT_INDEX)

        index_settings = {
            "number_of_shards": 1,
            "analysis": {
                "filter": {
                    "autocomplete_filter": {
                        "type": "edge_ngram",
                        "min_gram": 1,
                        "max_gram": 20
                    },
                },
                "analyzer": {
                    "autocomplete": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "asciifolding",
                            "stop",
                            "autocomplete_filter"
                        ]
                    },
                    "custom_search_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "asciifolding"
                        ]
                    },
                }
            }
        }

        item_index_settings = {
            "settings": index_settings,

            "mappings": {
                "_source": {"enabled": True},
                "properties": {
                    "id": {
                        "type": "integer"
                    },
                    "title": {
                        "type": "text",
                        "analyzer": "autocomplete",
                        "search_analyzer": "custom_search_analyzer",
                        "boost": 2
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "autocomplete",
                        "search_analyzer": "custom_search_analyzer"
                    },
                    "language": {
                        "type": "text"
                    },
                    "url": {
                        "type": "text",
                        "index": False
                    },
                    "in_trash": {
                        "type": "boolean",
                    },
                    "hidden": {
                        "type": "boolean",
                    },
                }
            }
        }

        project_index_settings = {
            "settings": index_settings,

            "mappings": {
                "_source": {"enabled": True},
                "properties": {
                    "id": {
                        "type": "integer"
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "autocomplete",
                        "search_analyzer": "custom_search_analyzer",
                        "boost": 2
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "autocomplete",
                        "search_analyzer": "custom_search_analyzer"
                    },
                    "url": {
                        "type": "text",
                        "index": False
                    },
                    "hidden": {
                        "type": "boolean",
                    },
                }
            }
        }

        indicies_client.create(settings.ES_ITEM_INDEX, body=item_index_settings)
        indicies_client.create(settings.ES_PROJECT_INDEX, body=project_index_settings)

        items = Item.all_the_objects \
            .select_related('project') \
            .prefetch_related('channels', 'tags', 'targets')
        for item in items.iterator():
            try:
                settings.ES_CLIENT.create(
                    settings.ES_ITEM_INDEX,
                    item.id,
                    ItemSearchDocTypeSerializer(item, context={'rebuild_index': True}).data
                )
                logger.info('Indexed item %d' % item.id)
            except Exception as e:
                logger.error('Indexation went wrong for item %d : %s' % (item.id, e))

        projects = Project.all_the_objects.prefetch_related('channels', 'tags', 'targets')
        for project in projects.iterator():
            try:
                settings.ES_CLIENT.create(
                    settings.ES_PROJECT_INDEX,
                    project.id,
                    ProjectSearchDocTypeSerializer(project, context={'rebuild_index': True}).data
                )
                logger.info('Indexed project %d' % project.id)
            except Exception as e:
                logger.error('Indexation went wrong for project %d : %s' % (project.id, e))

        logger.info(f"[Command End] {' '.join(sys.argv[1:])}")
