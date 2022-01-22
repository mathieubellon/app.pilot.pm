from django.utils.translation import ugettext_lazy as _

from pilot.workflow.models import WorkflowState

INITIAL_WORKFLOW_STATES = (
    dict(
        label=_("Brouillon"),
        order=0,
        color='#C62828'
    ),
    dict(
        label=_("A valider"),
        order=1,
        color='#EF6C00'
    ),
    dict(
        label=_("A publier"),
        order=2,
        color='#558B2F'
    ),
    dict(
        label=_("En ligne"),
        order=3,
        color='#CFD8DC'
    ),
    dict(
        label=_("Hors-ligne"),
        order=4,
        color='#000000'
    ),
)


def init_workflow_states_for_desk(desk):
    for dict_state in INITIAL_WORKFLOW_STATES:
        WorkflowState.objects.create(desk=desk, created_by_id=1, **dict_state)
