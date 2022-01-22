from rest_framework import routers
from pilot.integrations.public_endpoints.beta import api as api_beta

integrations_endpoints_router_beta = routers.SimpleRouter()
integrations_endpoints_router_beta.register('channels', api_beta.IntegrationsChannelViewSet, basename='integrations-channels')
integrations_endpoints_router_beta.register('items', api_beta.IntegrationsItemViewSet, basename='integrations-items')
integrations_endpoints_router_beta.register('item_types', api_beta.IntegrationsItemTypeViewSet, basename='integrations-item-types')
integrations_endpoints_router_beta.register('projects', api_beta.IntegrationsProjectViewSet, basename='integrations-projects')
integrations_endpoints_router_beta.register('workflow_states', api_beta.IntegrationsWorkflowStateViewSet, basename='integrations-workflow-states')

