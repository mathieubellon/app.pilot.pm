import _ from "lodash"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"

export const FEED_TYPE_ACTIVITY_STREAM = "activity_stream"
export const FEED_TYPE_ITEM_SAVED_FILTER = "item_saved_filter"

export default {
    namespaced: true,
    state: {
        notificationFeeds: [],
        blinkerNotificationFeed: null,
    },
    mutations: {
        setNotificationFeeds(state, notificationFeeds) {
            state.notificationFeeds = notificationFeeds
        },
        prependToNotificationFeeds(state, notificationFeed) {
            state.notificationFeeds = [notificationFeed, ...state.notificationFeeds]
        },
        removeNotificationFeed(state, notificationFeed) {
            state.notificationFeeds = state.notificationFeeds.filter(
                (nf) => nf.id != notificationFeed.id,
            )
        },
        updateNotificationFeedInList(state, updatedNotificationFeed) {
            state.notificationFeeds = state.notificationFeeds.map((nf) =>
                nf.id == updatedNotificationFeed.id ? updatedNotificationFeed : nf,
            )
        },
        setBlinkerNotificationFeed(state, notificationFeed) {
            state.blinkerNotificationFeed = notificationFeed
        },
    },
    getters: {
        // Search for an existingNotification feed related to a given savedFilter
        getExistingNotificationFeed: (state) => (savedFilter) => {
            return _.find(state.notificationFeeds, (nf) => nf.saved_filter.id == savedFilter.id)
        },
    },
    actions: {
        fetchNotificationFeeds({ state, commit }) {
            return $httpX({
                name: "fetchNotificationFeeds",
                commit: commit,
                url: urls.notificationFeeds,
                method: "GET",
            }).then((response) => {
                commit("setNotificationFeeds", response.data)
            })
        },
        createFeedForSavedFilter({ state, getters, commit, dispatch }, savedFilter) {
            // The feed does not already exists, we can proceed to actually create it
            return $httpX({
                name: "createFeedForSavedFilter",
                commit: commit,
                url: urls.notificationFeeds,
                method: "POST",
                data: {
                    feed_type: FEED_TYPE_ITEM_SAVED_FILTER,
                    saved_filter_id: savedFilter.id,
                },
            }).then((response) => {
                commit("prependToNotificationFeeds", response.data)
                return response.data
            })
        },
        deleteNotificationFeed({ commit }, notificationFeed) {
            return $httpX({
                name: "deleteNotificationFeed",
                commit,
                url: urls.notificationFeeds.format({ id: notificationFeed.id }),
                method: "DELETE",
            }).then((response) => {
                // Remove the publicSharedFilter from the list
                commit("removeNotificationFeed", notificationFeed)
            })
        },
        toggleFeedAppPreference({ commit }, notificationFeed) {
            $httpX({
                name: "toggleFeedAppPreference",
                commit: commit,
                url: urls.notificationFeeds.format({ id: notificationFeed.id }),
                method: "PATCH",
                data: {
                    display_in_app: !notificationFeed.display_in_app,
                },
            }).then((response) => {
                commit("updateNotificationFeedInList", response.data)
            })
        },
        toggleFeedEmailPreference({ commit }, notificationFeed) {
            $httpX({
                name: "toggleFeedEmailPreference",
                commit: commit,
                url: urls.notificationFeeds.format({ id: notificationFeed.id }),
                method: "PATCH",
                data: {
                    send_email: !notificationFeed.send_email,
                },
            }).then((response) => {
                commit("updateNotificationFeedInList", response.data)
            })
        },
        blinkNotificationFeed({ commit }, notificationFeed) {
            commit("setBlinkerNotificationFeed", notificationFeed)
            setTimeout(() => commit("setBlinkerNotificationFeed"), 6000)
        },
    },
}
