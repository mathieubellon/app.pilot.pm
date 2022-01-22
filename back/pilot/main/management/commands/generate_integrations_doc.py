import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from settings.base import backend_path

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    requires_system_checks = False

    def handle(self, *args, **kwargs):
        settings.SWAGGER_SETTINGS['DEFAULT_INFO'] = 'doc.open_api.integrations_api_info'

        from drf_yasg.management.commands import generate_swagger
        generate_swagger.Command().handle(
            output_file=backend_path('doc/integrations_openapi.json'),
            overwrite=True,
            format='json',
            api_url=None,
            mock=None,
            api_version=None,
            user=None,
            private=None,
            generator_class_name='doc.open_api.IntegrationAPIOpenAPISchemaGenerator'
        )

