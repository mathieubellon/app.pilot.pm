import logging

from django.conf import settings

from pilot.search.api.serializers import ItemSearchDocTypeSerializer

logger = logging.getLogger(__name__)


def reindex_item(sender, instance, **kwargs):
    if not settings.ES_DISABLED:
        item = instance

        try:
            settings.ES_CLIENT.index(settings.ES_ITEM_INDEX,
                                     ItemSearchDocTypeSerializer(item).data,
                                     id=item.id)
        except:
            logger.error("[ES Indexing Error] Could not index Item (id={})"
                         "".format(item.id),
                         exc_info=True)
