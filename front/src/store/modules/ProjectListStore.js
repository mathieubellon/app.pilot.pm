import _ from "lodash"
import Vue from "vue"
import { $httpX } from "@js/ajax.js"
import { EVENTS, mapEvents } from "@js/events"
import { applyScrollPos } from "@js/bootstrap"

export default {
    namespaced: true,
    state: () => ({
        apiSource: null,
        projects: [],
        pagination: null,
        savedQueries: {},
    }),
    mutations: {
        setApiSource(state, apiSource) {
            state.apiSource = apiSource
        },
        setProjects(state, projects) {
            state.projects = projects
        },
        prependProject(state, project) {
            state.projects.unshift(project)
        },
        setPagination(state, pagination) {
            state.pagination = pagination
        },
        saveQuery(state, { routeName, query }) {
            Vue.set(state.savedQueries, routeName, query)
        },
    },
    actions: {
        fetchProjectList({ state, commit, rootState }) {
            return $httpX({
                name: "fetchProjectList",
                commit,
                url: state.apiSource.endpoint,
                // Not supported in IE11 :-(
                //params: state.queryParamSerializer.getURLSearchParams()
                params: state.apiSource.queryParamSerializer.params,
            })
                .then((response) => {
                    commit("setPagination", _.omit(response.data, "objects"))
                    commit("setProjects", response.data.objects)
                    setTimeout(() => applyScrollPos(rootState.route), 25)
                })
                .catch((errors) => {
                    commit("setPagination", null)
                })
        },

        /***********************
         * Listeners to store events
         ************************/

        ...mapEvents({
            [EVENTS.projectCreated]({ commit }, project) {
                commit("prependProject", project)
            },
        }),
    },
}
