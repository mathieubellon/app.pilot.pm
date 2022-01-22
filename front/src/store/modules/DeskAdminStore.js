import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"

export default {
    namespaced: true,
    state: () => ({
        desk: {},
        exports: [],
        exportLaunched: false,
        availableLanguages: [],
    }),
    mutations: {
        setDesk(state, desk) {
            state.desk = desk
        },
        setExports(state, exports) {
            state.exports = exports
        },
        prependToExports(state, newExport) {
            state.exports.unshift(newExport)
        },
        setExportLaunched(state, exportLaunched) {
            state.exportLaunched = exportLaunched
        },
        setAvailableLanguages(state, availableLanguages) {
            state.availableLanguages = availableLanguages
        },
    },
    actions: {
        fetchDesk({ state, commit, getters }) {
            return $httpX({
                name: "fetchDesk",
                commit,
                url: urls.desksCurrent,
                method: "GET",
            }).then((response) => {
                commit("setDesk", response.data)
            })
        },
        fetchExports({ state, commit, getters }) {
            $httpX({
                name: "fetchExports",
                commit,
                url: urls.exports,
                method: "GET",
            }).then((response) => {
                commit("setExports", response.data)
            })
        },
        launchExport({ state, commit, getters }) {
            $httpX({
                name: "launchExport",
                commit,
                url: urls.exports,
                method: "POST",
            }).then((response) => {
                commit("prependToExports", response.data)
                commit("setExportLaunched", true)
            })
        },
        fetchLanguages({ state, commit, getters }) {
            return $httpX({
                name: "fetchLanguages",
                commit,
                url: urls.languagesChoices,
                method: "GET",
            }).then((response) => {
                commit("setAvailableLanguages", response.data)
            })
        },
    },
}
