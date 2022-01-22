import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import { EVENTS, dispatchEvent } from "@js/events"

export default {
    namespaced: true,
    state: () => ({
        workflowStates: [],
    }),
    mutations: {
        setWorkflowStates(state, workflowStates) {
            state.workflowStates = workflowStates
        },
        appendToWorkflowStates(state, workflowState) {
            state.workflowStates.push(workflowState)
        },
        updateWorkflowState(state, workflowState) {
            state.workflowStates = state.workflowStates.map((oldWorkflowState) =>
                oldWorkflowState.id == workflowState.id ? workflowState : oldWorkflowState,
            )
        },
        removeWorkflowState(state, workflowState) {
            state.workflowStates = state.workflowStates.filter((t) => t.id != workflowState.id)
        },
    },
    actions: {
        fetchWorkflowStates({ commit }) {
            $httpX({
                name: "fetchWorkflowStates",
                method: "GET",
                commit,
                url: urls.workflowStates,
            }).then((response) => {
                commit("setWorkflowStates", response.data)
            })
        },
        deleteWorkflowState({ commit }, workflowState) {
            return $httpX({
                name: "deleteWorkflowState",
                commit,
                method: "DELETE",
                url: urls.workflowStates.format({ id: workflowState.id }),
            }).then((response) => {
                // Remove the taskGroup from the list
                commit("removeWorkflowState", workflowState)
                dispatchEvent(EVENTS.workflowStateDeleted, workflowState)
            })
        },
        setWorkflowStatesOrder({ state, commit }, newWorkflowStatesOrder) {
            $httpX({
                commit,
                name: "setWorkflowStatesOrder",
                method: "POST",
                url: urls.workflowStatesSetOrder,
                data: newWorkflowStatesOrder,
            }).then((response) => {
                commit("setWorkflowStates", response.data)
                dispatchEvent(EVENTS.workflowStateSorted, this.workflowStates)
            })
        },
    },
}
