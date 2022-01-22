from rest_framework import routers

from pilot.workflow.api import api

workflow_api_router = routers.SimpleRouter()
workflow_api_router.register('workflow/states', api.WorkflowStateViewSet, basename='workflow-states')
