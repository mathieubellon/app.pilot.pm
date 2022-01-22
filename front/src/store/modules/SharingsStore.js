import urls from "@js/urls"
import { $httpX } from "@js/ajax"

export default {
    namespaced: true,
    state: {
        // Sharing resource
        sharings: [],
    },
    mutations: {
        setSharings(state, sharings) {
            state.sharings = sharings
        },
        prependToSharings(state, sharing) {
            state.sharings = [sharing, ...state.sharings]
        },
        removeSharing(state, sharing) {
            state.sharings = state.sharings.filter((s) => s.token != sharing.token)
        },
    },
    getters: {},
    actions: {
        fetchSharings({ state, getters, commit }, sharingTarget) {
            return $httpX({
                name: "fetchSharings",
                commit,
                url: urls.sharings,
                method: "GET",
                params: sharingTarget,
            }).then((response) => {
                commit("setSharings", response.data)
            })
        },
        createSharing({ state, getters, commit }, sharing) {
            return $httpX({
                name: "createSharing",
                commit,
                url: urls.sharings,
                method: "POST",
                data: sharing,
            }).then((response) => {
                commit("prependToSharings", response.data)
            })
        },
        deactivateSharing({ state, getters, commit }, sharing) {
            return $httpX({
                name: `deactivateSharing-${sharing.token}`,
                commit,
                url: urls.sharingsDeactivate.format({
                    token: sharing.token,
                }),
                method: "POST",
            }).then((response) => {
                commit("removeSharing", response.data)
            })
        },
    },
}
