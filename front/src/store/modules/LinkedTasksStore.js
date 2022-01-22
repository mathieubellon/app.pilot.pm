import _ from "lodash"
import Vue from "vue"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import { EVENTS, mapEvents, dispatchEvent } from "@js/events"

export default {
    namespaced: true,
    state: () => ({
        linkedTasks: [],
        contentType: null,
        objectId: null,
        taskToEdit: null,
        // Keep track of fields that are currently being saved
        // {fieldName : true/false}
        fieldsCurrentlyUpdating: {},
    }),
    mutations: {
        initLinkedTasksStore(state, { contentType, objectId }) {
            state.contentType = contentType
            state.objectId = objectId
        },
        setLinkedTasks(state, linkedTasks) {
            state.linkedTasks = linkedTasks
        },
        updateLinkedTask(state, task) {
            state.linkedTasks = state.linkedTasks.map((oldTask) => {
                if (oldTask.id == task.id) {
                    return task
                } else {
                    // If the updated task has been set as is_publication,
                    // then the old publication task is not is_publication anymore
                    if (task.is_publication && oldTask.is_publication) {
                        oldTask.is_publication = false
                    }
                    return oldTask
                }
            })
            if (state.taskToEdit && task.id == state.taskToEdit.id) {
                state.taskToEdit = task
            }
        },
        removeLinkedTask(state, linkedTask) {
            state.linkedTasks = state.linkedTasks.filter((task) => task.id != linkedTask.id)
        },
        setTaskToEdit(state, taskToEdit) {
            state.taskToEdit = taskToEdit
        },
        startFieldsCurrentlyUpdating(state, fields) {
            for (let fieldName in fields) {
                Vue.set(state.fieldsCurrentlyUpdating, fieldName, true)
            }
        },
        stopFieldsCurrentlyUpdating(state, fields) {
            for (let fieldName in fields) {
                Vue.set(state.fieldsCurrentlyUpdating, fieldName, false)
            }
        },
    },
    getters: {
        publicationTask(state) {
            return _.find(state.linkedTasks, (t) => t.is_publication)
        },
        linkedTasksTodo(state) {
            if (!state.linkedTasks) return []
            return state.linkedTasks.filter((linkedTask) => !linkedTask.done)
        },
        currentTaskTodo(state, getters) {
            return getters.linkedTasksTodo.length > 0 ? getters.linkedTasksTodo[0] : null
        },
        getNextTaskToDo: (state) => (task) => {
            let index = _.findIndex(state.linkedTasks, (linkedTask) => linkedTask.id == task.id)
            if (
                index > -1 &&
                index < state.linkedTasks.length - 1 &&
                !state.linkedTasks[index + 1].done
            ) {
                return state.linkedTasks[index + 1]
            }
            return null
        },
    },
    actions: {
        fetchLinkedTasks({ state, commit }) {
            return $httpX({
                name: "linkedTasks",
                commit,
                url: urls.tasksLinked.format({
                    contentTypeId: state.contentType.id,
                    objectId: state.objectId,
                }),
            }).then((response) => {
                commit("setLinkedTasks", response.data)
            })
        },
        createTask({ state, commit, dispatch }, task) {
            return $httpX({
                name: "createTask",
                commit,
                method: "POST",
                url: urls.tasks,
                data: {
                    ...task,
                    content_type_id: state.contentType.id,
                    object_id: state.objectId,
                },
            }).then((response) => {
                dispatchEvent(EVENTS.taskCreated, { task: response.data })
            })
        },
        partialUpdateTask({ state, commit, dispatch }, taskData) {
            let taskBefore = _.clone(state.linkedTasks.find((t) => t.id == taskData.id))
            commit("startFieldsCurrentlyUpdating", taskData)
            return $httpX({
                name: "partialUpdateTask" + taskData.id,
                commit,
                method: "PATCH",
                url: urls.tasks.format({ id: taskData.id }),
                data: taskData,
            })
                .then((response) => {
                    let task = response.data
                    dispatch(
                        EVENTS.taskUpdated,
                        {
                            task,
                            taskBefore,
                        },
                        { root: true },
                    )
                    return task
                })
                .finally(() => {
                    commit("stopFieldsCurrentlyUpdating", taskData)
                })
        },
        saveCurrentTaskOrder({ state, commit }) {
            let tasksOrder = state.linkedTasks.map((task, index) => ({ id: task.id, order: index }))

            return $httpX({
                name: "saveCurrentTaskOrder",
                commit,
                method: "POST",
                url: urls.tasksSetOrder,
                data: tasksOrder,
            }).then((response) => {
                commit("setLinkedTasks", response.data)
            })
        },
        deleteTask({ state, commit, dispatch }, { task, notify }) {
            return $httpX({
                name: "deleteTask" + task.id,
                commit,
                method: "DELETE",
                url: urls.tasks.format({ id: task.id }),
            }).then((response) => {
                dispatchEvent(EVENTS.taskDeleted, { task })

                if (notify && task.assignees.length > 0) {
                    dispatch("sendNotification", {
                        task: task,
                        type: "deleted",
                    })
                }
            })
        },
        sendNotification({ state, commit, dispatch }, { task, type }) {
            return $httpX({
                name: "sendTaskNotification",
                commit,
                method: "POST",
                url: urls.tasksSendNotifications.format({ id: task.id }),
                data: {
                    type: type,
                },
            }).then((response) => {
                setTimeout(() => {
                    commit("loading/resetLoading", "sendTaskNotification", { root: true })
                }, 2000)
            })
        },
        importTaskGroup({ state, commit, dispatch }, taskGroup) {
            return $httpX({
                name: "importTaskGroup",
                commit,
                method: "POST",
                url: urls.tasksImportTaskGroup,
                data: {
                    task_group_id: taskGroup.id,
                    content_type_id: state.contentType.id,
                    object_id: state.objectId,
                },
            }).then((response) => {
                commit("setLinkedTasks", response.data)
            })
        },

        /***********************
         * Listeners to store events
         ************************/

        ...mapEvents({
            [EVENTS.taskCreated]({ state, commit }, { task }) {
                commit("setLinkedTasks", [task, ...state.linkedTasks])
            },

            [EVENTS.taskUpdated]({ commit }, { task }) {
                commit("updateLinkedTask", task)
            },

            [EVENTS.taskDeleted]({ commit, dispatch }, { task }) {
                // Remove the task from the list
                commit("removeLinkedTask", task)
                dispatch("saveCurrentTaskOrder")
            },
        }),
    },
}
