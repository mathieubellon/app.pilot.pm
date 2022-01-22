import logging

from django.conf import settings

from pilot.search.api.serializers import ProjectSearchDocTypeSerializer

logger = logging.getLogger(__name__)


def reindex_project(sender, instance, **kwargs):
    if not settings.ES_DISABLED:
        project = instance

        try:
            settings.ES_CLIENT.index(settings.ES_PROJECT_INDEX,
                                     ProjectSearchDocTypeSerializer(project).data,
                                     id=project.id)
        except:
            logger.error("[ES Indexing Error] Could not index Project (id={})"
                         "".format(project.id),
                         exc_info=True)
