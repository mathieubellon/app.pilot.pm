from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from doc.internal_api_description import INTERNAL_API_DESCRIPTION


class APISwaggerAutoSchema(SwaggerAutoSchema):
    def get_summary_and_description(self):
        """Return an operation summary and description determined from the view's docstring.

        :return: summary and description
        :rtype: (str,str)
        """
        description = self.overrides.get('operation_description', None)
        summary = self.overrides.get('operation_summary', None)
        if description is None:
            description = self._sch.get_description(self.path, self.method) or ''
            description = description.strip().replace('\r', '')

        return summary, description


class InternalAPIOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    """
    A generator that list only internal API path, excluding integration API.
    """
    def should_include_endpoint(self, path, method, view, public):
        if not super(InternalAPIOpenAPISchemaGenerator, self).should_include_endpoint(path, method, view, public):
            return False

        return path.startswith('/api')

    def determine_path_prefix(self, paths):
        return '/api/'


internal_api_schema_view = get_schema_view(
    openapi.Info(
        title="Pilot internal API",
        description=INTERNAL_API_DESCRIPTION,
        default_version=''
    ),
    public=True,
    generator_class=InternalAPIOpenAPISchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)


class IntegrationAPIOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    """
    A generator that list only integration API path, excluding internal API.
    """
    def should_include_endpoint(self, path, method, view, public):
        if not super(IntegrationAPIOpenAPISchemaGenerator, self).should_include_endpoint(path, method, view, public):
            return False

        return path.startswith('/integrations')

    def determine_path_prefix(self, paths):
        return '/integrations/beta/'


integrations_api_info = openapi.Info(
    title="Pilot integration API",
    description="TODO",
    default_version='beta'
)
integrations_api_schema_view = get_schema_view(
    integrations_api_info,
    public=True,
    generator_class=IntegrationAPIOpenAPISchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)
