import _ from "lodash"
import Vue from "vue"
import { $httpX } from "@js/ajax.js"
import { EVENTS, mapEvents } from "@js/events"
import { applyScrollPos } from "@js/bootstrap"

export default {
    namespaced: true,
    state: {
        apiSource: null,
        channels: [],
        pagination: null,
        savedQueries: {},
    },
    mutations: {
        setApiSource(state, apiSource) {
            state.apiSource = apiSource
        },
        setChannels(state, channels) {
            state.channels = channels
        },
        prependChannel(state, channel) {
            state.channels.unshift(channel)
        },
        setPagination(state, pagination) {
            state.pagination = pagination
        },
        saveQuery(state, { routeName, query }) {
            Vue.set(state.savedQueries, routeName, query)
        },
    },
    actions: {
        fetchChannelList({ state, rootState, commit }) {
            return $httpX({
                name: "fetchChannelList",
                commit,
                url: state.apiSource.endpoint,
                // Not supported in IE11 :-(
                //params: state.queryParamSerializer.getURLSearchParams()
                params: state.apiSource.queryParamSerializer.params,
            })
                .then((response) => {
                    commit("setPagination", _.omit(response.data, "objects"))
                    commit("setChannels", response.data.objects)
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
            [EVENTS.channelCreated]({ commit }, project) {
                commit("prependChannel", project)
            },
        }),
    },
}
