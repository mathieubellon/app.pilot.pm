import Vue from "vue"

export default {
    namespaced: true,
    state: {
        openedOffPanels: {},
    },
    mutations: {
        openOffPanel(state, name) {
            Vue.set(state.openedOffPanels, name, true)
        },
        closeOffPanel(state, name) {
            Vue.set(state.openedOffPanels, name, false)
        },
        closeAllOffPanels(state) {
            state.openedOffPanels = {}
        },
    },
}
