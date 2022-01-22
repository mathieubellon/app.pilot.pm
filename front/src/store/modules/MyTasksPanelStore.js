import _ from "lodash"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import { EVENTS, mapEvents } from "@js/events"

const UNDONE = "undone"
const DONE = "done"

function createTasksListData() {
    return {
        tasks: [],
        pagination: null,
    }
}

export default {
    namespaced: true,
    state: {
        undone: createTasksListData(),
        done: createTasksListData(),
    },
    mutations: {
        setTasks(state, { tasks, listName }) {
            state[listName].tasks = tasks
        },
        prependTask(state, { task, listName }) {
            state[listName].tasks.unshift(task)
        },
        appendToTasks(state, { tasks, listName }) {
            state[listName].tasks = state[listName].tasks.concat(tasks)
        },
        removeTask(state, { task, listName }) {
            state[listName].tasks = state[listName].tasks.filter((_task) => _task.id !== task.id)
        },
        incrementCount(state, listName) {
            return state[listName].pagination.count++
        },
        decrementCount(state, listName) {
            return state[listName].pagination.count--
        },
        setPagination(state, { pagination, listName }) {
            state[listName].pagination = pagination
        },
    },
    getters: {
        undoneCount(state) {
            return _.get(state, "undone.pagination.count", "?")
        },
        doneCount(state) {
            return _.get(state, "done.pagination.count", "?")
        },
    },
    actions: {
        fetchTasks({ state, commit }, { listName, append = false }) {
            let page, fetchName
            if (append) {
                page = state[listName].pagination.next
                fetchName = "appendTasks"
            } else {
                page = 1
                fetchName = "fetchTasks"
                commit("setPagination", { listName, pagination: null })
            }

            return $httpX({
                name: fetchName,
                commit,
                url: urls.tasksOfCurrentUser.format({ listName }),
                params: { page },
            })
                .then((response) => {
                    commit("setPagination", {
                        listName,
                        pagination: _.omit(response.data, "objects"),
                    })
                    let tasks = response.data.objects
                    if (append) commit("appendToTasks", { listName, tasks })
                    else commit("setTasks", { listName, tasks })
                })
                .catch((errors) => {
                    commit("setPagination", { listName, pagination: null })
                })
        },
        toggleTaskDone({ dispatch, commit }, task) {
            let taskBefore = _.clone(task)
            let loadingName = "toggleTaskDone" + task.id
            return $httpX({
                name: loadingName,
                commit,
                method: "PATCH",
                url: urls.tasks.format({ id: task.id }),
                data: {
                    done: !task.done,
                },
            }).then((response) => {
                task.done = !task.done

                let removeFrom, addTo
                if (task.done) {
                    removeFrom = UNDONE
                    addTo = DONE
                } else {
                    removeFrom = DONE
                    addTo = UNDONE
                }
                // Let 2 seconds to the user to see its modification
                // Then remove the task from the list
                setTimeout(() => {
                    commit("removeTask", {
                        task: task,
                        listName: removeFrom,
                    })
                    commit("prependTask", {
                        task: task,
                        listName: addTo,
                    })
                    commit("loading/resetLoading", loadingName, { root: true })
                }, 2000)
                // Update the counts
                commit("decrementCount", removeFrom)
                commit("incrementCount", addTo)

                dispatch(
                    EVENTS.taskUpdated,
                    {
                        task,
                        taskBefore,
                    },
                    { root: true },
                )
            })
        },
    },
}
