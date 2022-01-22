import moment from "moment"
import Vue from "vue"
import i18n from "@js/i18n"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"

function getProjectColor(project) {
    return project.category && project.category.color
}

export default {
    namespaced: true,
    state: {
        itemsApiSource: null,
        projectsApiSource: null,
        items: [],
        projects: [],
        savedQueries: {},
    },
    mutations: {
        setItemsApiSource(state, itemsApiSource) {
            state.itemsApiSource = itemsApiSource
        },
        setProjectsApiSource(state, projectsApiSource) {
            state.projectsApiSource = projectsApiSource
        },
        setItems(state, items) {
            state.items = items
        },
        prependItem(state, item) {
            state.items.unshift(item)
        },
        updateItemInList(state, item) {
            state.items = state.items.map((oldItem) => (oldItem.id == item.id ? item : oldItem))
        },
        removeItemsById(state, itemIds) {
            state.items = state.items.filter((i) => !itemIds.includes(i.id))
        },
        setProjects(state, projects) {
            state.projects = projects
        },
        prependProject(state, project) {
            state.projects.unshift(project)
        },
        saveQuery(state, { routeName, query }) {
            Vue.set(state.savedQueries, routeName, query)
        },
    },
    getters: {
        displayTasks(state, getters, rootState, rootGetters) {
            if (rootState.sharing) {
                return rootState.sharing.saved_filter.display_tasks
            }
            if (
                rootGetters.currentRouteName == "calendar-filter" &&
                rootGetters["savedFilter/selectedSavedFilter"]
            )
                return rootGetters["savedFilter/selectedSavedFilter"].display_tasks
            else
                return (
                    rootState.users.me.config_calendar &&
                    rootState.users.me.config_calendar.displayTasks
                )
        },
        displayProjects(state, getters, rootState, rootGetters) {
            if (rootState.sharing) {
                return rootState.sharing.saved_filter.display_projects
            } else if (
                rootGetters.currentRouteName == "calendar-filter" &&
                rootGetters["savedFilter/selectedSavedFilter"]
            )
                return rootGetters["savedFilter/selectedSavedFilter"].display_projects
            else
                return (
                    rootState.users.me.config_calendar &&
                    rootState.users.me.config_calendar.displayProjects
                )
        },
        displayAllTasks(state, getters, rootState, rootGetters) {
            if (rootState.sharing) {
                return rootState.sharing.saved_filter.display_all_tasks
            } else if (
                rootGetters.currentRouteName == "calendar-filter" &&
                rootGetters["savedFilter/selectedSavedFilter"]
            )
                return rootGetters["savedFilter/selectedSavedFilter"].display_all_tasks
            else
                return (
                    rootState.users.me.config_calendar &&
                    rootState.users.me.config_calendar.displayAllTasks
                )
        },
        projectEvents(state, getters, rootState) {
            return state.projects.map((project) => {
                let color = getProjectColor(project)
                // Fullcalendar use an EXCLUSIVE end date (see doc),
                // so we need to shift the end date by one day
                let end = moment(project.end).add(1, "days")
                return {
                    type: "project",
                    id: project.id,
                    // Project are handled by the router on the standard Calendar.
                    // BUT we still set it here so a ctrl+click will still correctly open a new tab on this url
                    url: project.url,
                    project: project,
                    title: project.title,
                    start: project.start,
                    end: end,
                    editable: false, // Disallow drag'n'drop of projects,
                    startEditable: false, // Disallow drag'n'drop of projects,
                    className: "fc-event-project",
                    backgroundColor: color,
                    borderColor: color,
                    textColor: "#fff",
                }
            })
        },
        taskEvents(state, getters) {
            let taskEvents = []
            for (let item of state.items) {
                for (let task of item.tasks || []) {
                    if (!task.deadline) {
                        continue
                    }
                    /*
                    if( !getters.displayAllTasks && !task.show_in_publishing_calendar){
                        continue
                    }
                    */
                    if (!getters.displayAllTasks && !task.is_publication) {
                        continue
                    }

                    let itemTitle = item.title ? item.title : i18n.t("contentWithoutTitle")
                    let title = getters.displayAllTasks
                        ? "[" + task.name + "] " + itemTitle
                        : itemTitle
                    taskEvents.push({
                        type: "task",
                        id: task.id,
                        // Item are handled by the router on the standard Calendar.
                        // BUT we still set it here so a ctrl+click will still correctly open a new tab on this url
                        url: item.url,
                        task: task,
                        item: item,
                        title: title,
                        start: task.deadline,
                        editable: true, // Allow drag'n'drop of tasks
                        className: "fc-event-item",
                        borderColor: item.project ? getProjectColor(item.project) : null,
                        textColor: item.workflow_state ? item.workflow_state.color : null,
                    })
                }
            }
            return taskEvents
        },
        eventSources(state, getters) {
            let eventSources = []
            if (getters.displayProjects) {
                eventSources.push(getters.projectEvents)
            }
            if (getters.displayTasks) {
                eventSources.push(getters.taskEvents)
            }
            return eventSources
        },
    },
    actions: {
        fetchCalendarEvents({ dispatch }) {
            dispatch("fetchItemsCalendar")
            dispatch("fetchProjectsCalendar")
        },
        fetchItemsCalendar({ state, commit, getters, rootState }) {
            /*
            let urlParams = {},
                itemsUrl = urls.itemsForCalendar

            if( rootState.sharing){
                itemsUrl = urls.itemsSharedForCalendar
                urlParams.token = rootState.sharing.token
            }
             */

            return $httpX({
                name: "fetchItemsCalendar",
                commit,
                url: state.itemsApiSource.endpoint,
                params: state.itemsApiSource.queryParamSerializer.params,
            }).then((response) => {
                commit("setItems", response.data)
            })
        },
        fetchProjectsCalendar({ state, commit, getters, rootState }) {
            /*
            let urlParams = {},
                projectsUrl = urls.projectsForCalendar

            if( rootState.sharing){
                projectsUrl = urls.projectsSharedForCalendar
                urlParams.token = rootState.sharing.token
            }
             */

            return $httpX({
                name: "fetchProjectsCalendar",
                commit,
                url: state.projectsApiSource.endpoint,
                params: state.projectsApiSource.queryParamSerializer.params,
            }).then((response) => {
                commit("setProjects", response.data)
            })
        },
        updateTaskDeadline({ state, commit, getters }, { taskId, deadline }) {
            return $httpX({
                method: "PATCH",
                name: "updateTaskDeadline",
                commit,
                url: urls.tasks.format({ id: taskId }),
                data: { deadline },
            })
        },
    },
}
