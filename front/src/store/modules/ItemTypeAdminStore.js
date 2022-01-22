import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"

export default {
    namespaced: true,
    state: () => ({
        itemTypes: [],
        contentFieldSpecs: [],
    }),
    mutations: {
        setItemTypes(state, itemTypes) {
            state.itemTypes = itemTypes
        },
        prependItemType(state, itemType) {
            state.itemTypes.push(itemType)
        },
        partialUpdateItemTypeInList(state, itemType) {
            state.itemTypes = state.itemTypes.map((oldItemType) =>
                oldItemType.id == itemType.id ? itemType : oldItemType,
            )
        },
        removeItemType(state, itemType) {
            state.itemTypes = state.itemTypes.filter((it) => it.id != itemType.id)
        },
        setContentFieldSpecs(state, contentFieldSpecs) {
            state.contentFieldSpecs = contentFieldSpecs
        },
    },
    getters: {
        itemTypeId(state, getters, rootState) {
            return parseInt(rootState.route.params.id)
        },
        itemType(state, getters) {
            return state.itemTypes.find((it) => it.id == getters.itemTypeId) || {}
        },
    },
    actions: {
        fetchItemTypes({ commit }) {
            $httpX({
                name: "fetchItemTypes",
                method: "GET",
                commit,
                url: urls.itemTypes,
            }).then((response) => {
                commit("setItemTypes", response.data)
            })
        },
        partialUpdateItemType({ commit }, itemType) {
            $httpX({
                name: "partialUpdateItemType",
                commit: commit,
                url: urls.itemTypes.format({ id: itemType.id }),
                method: "PATCH",
                data: itemType,
            }).then((response) => {
                commit("partialUpdateItemTypeInList", response.data)
            })
        },
        deleteItemType({ commit }, itemType) {
            return $httpX({
                name: "deleteItemType",
                commit,
                method: "DELETE",
                url: urls.itemTypes.format({ id: itemType.id }),
            }).then((response) => {
                // Remove the taskGroup from the list
                commit("removeItemType", itemType)
            })
        },
        fetchContentFieldSpecs({ state, commit, getters }) {
            return $httpX({
                name: "fetchContentFieldSpecs",
                commit,
                url: urls.contentFieldSpecs,
                method: "GET",
            }).then((response) => {
                commit("setContentFieldSpecs", response.data)
            })
        },
    },
}
