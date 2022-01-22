import _ from "lodash"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"

import ActivityFeedStore from "@/store/modules/ActivityFeedStore.js"
import LinkedAssetsStore from "@/store/modules/LinkedAssetsStore.js"

export default {
    namespaced: true,
    modules: {
        activityFeed: ActivityFeedStore,
        linkedAssets: LinkedAssetsStore,
    },
    state: {
        wikiPage: {},
        wikiPagesList: [],

        wikiPageInEdition: null,
        wikiPageInEditionValidation: null,
    },
    mutations: {
        setWikiPage(state, wikiPage) {
            state.wikiPage = wikiPage
        },
        setWikiPagesList(state, wikiPagesList) {
            state.wikiPagesList = wikiPagesList
        },
        appendToWikiPagesList(state, wikiPage) {
            state.wikiPagesList = state.wikiPagesList.concat(wikiPage)
        },
        updateWikiPageInList(state, wikiPage) {
            state.wikiPagesList = state.wikiPagesList.map((oldWikiPage) =>
                oldWikiPage.id == wikiPage.id ? wikiPage : oldWikiPage,
            )
        },
        removeWikiPage(state, wikiPage) {
            state.wikiPagesList = state.wikiPagesList.filter((f) => f.id != wikiPage.id)
        },
        setWikiPageInEdition(state, wikiPageInEdition) {
            state.wikiPageInEdition = wikiPageInEdition
        },
        setWikiPageInEditionValidation(state, wikiPageInEditionValidation) {
            state.wikiPageInEditionValidation = wikiPageInEditionValidation
        },
    },
    getters: {
        wikiPageApiUrl(state, getters, rootState, rootGetters) {
            let routeName = rootGetters.currentRouteName
            if (routeName == "wikiHome") {
                return urls.wikiHomePage
            } else {
                return urls.wikiPages.format({ id: parseInt(rootState.route.params.id) })
            }
        },
    },
    actions: {
        fetchWikiPage({ commit, getters }) {
            return $httpX({
                commit,
                name: "fetchWikiPage",
                method: "GET",
                url: getters.wikiPageApiUrl,
                handle404: true,
            }).then((response) => {
                commit("setWikiPage", response.data)
                return response.data
            })
        },
        fetchWikiPagesList({ commit }) {
            return $httpX({
                commit,
                name: "fetchWikiPagesList",
                method: "GET",
                url: urls.wikiPages,
            }).then((response) => {
                commit("setWikiPagesList", response.data)
            })
        },
        createWikiPage({ commit }, wikiPage) {
            return $httpX({
                commit,
                name: "saveWikiPage",
                method: "POST",
                url: urls.wikiPages,
                data: wikiPage,
            }).then((response) => {
                let wikiPage = response.data
                commit("appendToWikiPagesList", wikiPage)
                commit("setWikiPage", wikiPage)
            })
        },
        updateWikiPage({ commit }, wikiPage) {
            return $httpX({
                commit,
                name: "saveWikiPage",
                method: "PUT",
                url: urls.wikiPages.format({ id: wikiPage.id }),
                data: wikiPage,
            }).then((response) => {
                let wikiPage = response.data
                commit("updateWikiPageInList", wikiPage)
                commit("setWikiPage", wikiPage)
            })
        },
        deleteWikiPage({ state, commit }, wikiPage) {
            return $httpX({
                name: "deleteWikiPage",
                commit,
                url: urls.wikiPages.format({ id: wikiPage.id }),
                method: "DELETE",
            }).then((response) => {
                // Remove the wikiPage from the list
                commit("removeWikiPage", wikiPage)
            })
        },

        startWikiPageCreation({ commit }) {
            commit("setWikiPageInEdition", {})
        },
        startWikiPageEdition({ state, commit }) {
            commit("setWikiPageInEdition", _.cloneDeep(state.wikiPage))
        },
    },
}
