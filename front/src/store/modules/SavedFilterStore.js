import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"

let fetchSavedFiltersPromise = false

export default {
    namespaced: true,
    state: () => ({
        savedFilters: [],
        lastSelectedSavedFilter: null,
        internalSharedFilters: [],
    }),
    mutations: {
        setSavedFilters(state, savedFilters) {
            state.savedFilters = savedFilters
        },
        appendSavedFilter(state, savedFilters) {
            state.savedFilters = [...state.savedFilters, savedFilters]
        },
        removeSavedFilter(state, savedFilter) {
            state.savedFilters = state.savedFilters.filter((sf) => sf.id != savedFilter.id)
        },
        updateSavedFilterInList(state, updatedSavedFilter) {
            state.savedFilters = state.savedFilters.map((sf) =>
                sf.id == updatedSavedFilter.id ? updatedSavedFilter : sf,
            )
        },
        setLastSelectedSavedFilter(state, savedFilter) {
            state.lastSelectedSavedFilter = savedFilter
        },
        setInternalSharedFilters(state, internalSharedFilters) {
            state.internalSharedFilters = internalSharedFilters
        },
        prependToInternalSharedFilters(state, internalSharedFilter) {
            state.internalSharedFilters = [internalSharedFilter, ...state.internalSharedFilters]
        },
    },
    getters: {
        isFilterTabOpen(state, getters, rootState) {
            return (
                rootState.route && rootState.route.name && rootState.route.name.includes("-filter")
            )
        },
        savedFilterId(state, getters, rootState) {
            return getters.isFilterTabOpen ? parseInt(rootState.route.params.id) : null
        },
        selectedSavedFilter(state, getters) {
            if (!getters.savedFilterId) {
                return null
            }
            return state.savedFilters.find((sf) => sf.id == getters.savedFilterId)
        },
        isInternalSharedSavedFilter(state, getters, rootState) {
            return (
                getters.selectedSavedFilter &&
                getters.selectedSavedFilter.user.id != rootState.users.me.id
            )
        },
    },
    actions: {
        fetchSavedFilters({ commit }) {
            if (!fetchSavedFiltersPromise) {
                fetchSavedFiltersPromise = $httpX({
                    name: "fetchSavedFilters",
                    commit: commit,
                    url: urls.savedFilters,
                    method: "GET",
                }).then((response) => {
                    commit("setSavedFilters", response.data)
                })
            }
            return fetchSavedFiltersPromise
        },
        partialUpdateSavedFilter({ commit }, savedFilterData) {
            return $httpX({
                name: "updateSavedFilter",
                commit,
                url: urls.savedFilters.format({ id: savedFilterData.id }),
                method: "PATCH",
                data: savedFilterData,
            }).then((response) => {
                commit("updateSavedFilterInList", response.data)
            })
        },
        deleteSavedFilter({ commit }, savedFilter) {
            return $httpX({
                name: "deleteSavedFilter",
                commit,
                url: urls.savedFilters.format({ id: savedFilter.id }),
                method: "DELETE",
            })
        },
        fetchInternalSharedFilters({ state, commit, getters }) {
            $httpX({
                name: "fetchInternalSharedFilters",
                commit: commit,
                url: urls.internalSharedFilters,
                params: { saved_filter: getters.savedFilterId },
                method: "GET",
            }).then((response) => {
                commit("setInternalSharedFilters", response.data)
            })
        },
    },
}
