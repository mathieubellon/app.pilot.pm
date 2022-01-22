import Vue from "vue"
import { getAxiosErrorMessage } from "@js/errors"

export default {
    namespaced: true,
    state: {
        loadingInProgress: {},
        loadingStatus: {},
        loadingErrors: {},
    },
    mutations: {
        startLoading(state, name) {
            Vue.set(state.loadingInProgress, name, true)
            Vue.set(state.loadingErrors, name, null)
        },
        stopLoadingSuccess(state, name) {
            Vue.set(state.loadingInProgress, name, false)
            Vue.set(state.loadingStatus, name, "success")
        },
        stopLoadingError(state, { name, error }) {
            Vue.set(state.loadingInProgress, name, false)
            Vue.set(state.loadingStatus, name, "error")
            Vue.set(state.loadingErrors, name, error)
        },
        resetLoading(state, name) {
            Vue.set(state.loadingInProgress, name, false)
            Vue.set(state.loadingStatus, name, null)
            Vue.set(state.loadingErrors, name, null)
        },
    },
    getters: {
        getErrorMessage: (state) => (name) => {
            return getAxiosErrorMessage(state.loadingErrors[name])
        },
    },
}
