import _ from "lodash"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"

export default {
    namespaced: true,
    state: () => ({
        taskGroups: [],
        currentTaskGroup: {
            tasks: [],
        },
    }),
    mutations: {
        setTaskGroups(state, taskGroups) {
            state.taskGroups = taskGroups
        },
        appendToTaskGroups(state, taskGroup) {
            state.taskGroups.push(taskGroup)
        },
        updateTaskGroup(state, taskGroup) {
            state.taskGroups = state.taskGroups.map((oldTaskGroup) =>
                oldTaskGroup.id == taskGroup.id ? taskGroup : oldTaskGroup,
            )
        },
        removeTaskGroup(state, taskGroup) {
            state.taskGroups = state.taskGroups.filter((t) => t.id != taskGroup.id)
        },

        setCurrentTaskGroup(state, currentTaskGroup) {
            state.currentTaskGroup = currentTaskGroup
        },
        setTaskTemplates(state, taskTemplates) {
            state.currentTaskGroup.tasks = taskTemplates
        },
        appendTaskTemplate(state, taskTemplate) {
            state.currentTaskGroup.tasks.push(taskTemplate)
        },
        updateTaskTemplate(state, taskTemplate) {
            state.currentTaskGroup.tasks = state.currentTaskGroup.tasks.map((oldTaskTemplate) => {
                if (oldTaskTemplate.id == taskTemplate.id) {
                    return taskTemplate
                } else {
                    // If the updated task template has been set as is_publication,
                    // then the old publication task is not is_publication anymore
                    if (taskTemplate.is_publication && oldTaskTemplate.is_publication) {
                        oldTaskTemplate.is_publication = false
                    }
                    return oldTaskTemplate
                }
            })
        },
        removeTaskTemplate(state, taskTemplate) {
            state.currentTaskGroup.tasks = state.currentTaskGroup.tasks.filter(
                (t) => t.id != taskTemplate.id,
            )
        },
    },
    actions: {
        fetchTaskGroups({ commit }) {
            $httpX({
                name: "fetchTaskGroups",
                method: "GET",
                commit,
                url: urls.tasksGroups,
            }).then((response) => {
                commit("setTaskGroups", response.data)
            })
        },
        deleteTaskGroup({ commit }, taskGroup) {
            return $httpX({
                name: "deleteTaskGroup" + taskGroup.id,
                commit,
                method: "DELETE",
                url: urls.tasksGroups.format({ id: taskGroup.id }),
            }).then((response) => {
                // Remove the taskGroup from the list
                commit("removeTaskGroup", taskGroup)
            })
        },

        setTaskTemplatesOrder({ state, commit }, newTaskTemplatesOrder) {
            $httpX({
                commit,
                name: "setTaskTemplatesOrder",
                method: "POST",
                url: urls.tasksTemplatesSetOrder,
                data: newTaskTemplatesOrder,
            }).then((response) => {
                commit("setTaskTemplates", response.data)
            })
        },
        deleteTaskTemplate({ commit }, taskTemplate) {
            return $httpX({
                name: "deleteTaskTemplate" + taskTemplate.id,
                commit,
                method: "DELETE",
                url: urls.tasksTemplates.format({ id: taskTemplate.id }),
            }).then((response) => {
                // Remove the taskGroup from the list
                commit("removeTaskTemplate", taskTemplate)
            })
        },
    },
}
