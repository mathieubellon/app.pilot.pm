import _ from "lodash"
import { $httpX } from "@js/ajax.js"
import Vue from "vue"
import { EVENTS, dispatchEvent, mapEvents } from "@js/events"
import { applyScrollPos } from "@js/bootstrap"

export default {
    namespaced: true,
    state: () => ({
        apiSource: null,
        items: [],
        pagination: null,
        savedQueries: {},
    }),
    mutations: {
        setApiSource(state, apiSource) {
            state.apiSource = apiSource
        },
        setItems(state, items) {
            state.items = items
        },
        prependItem(state, item) {
            state.items.unshift(item)
        },
        appendToItems(state, items) {
            state.items = state.items.concat(items)
        },
        updateItemInList(state, item) {
            state.items = state.items.map((oldItem) => (oldItem.id == item.id ? item : oldItem))
        },
        removeItemsById(state, itemIds) {
            state.items = state.items.filter((i) => !itemIds.includes(i.id))
        },
        setPagination(state, pagination) {
            state.pagination = pagination
        },
        saveQuery(state, { routeName, query }) {
            Vue.set(state.savedQueries, routeName, query)
        },
    },
    getters: {
        isItemListRoute(state, getters, rootState, rootGetters) {
            let routeName = rootGetters.currentRouteName
            return (
                routeName.startsWith("itemList") ||
                routeName == "projectDetail-informations" ||
                routeName == "channelDetail-informations"
            )
        },
    },
    actions: {
        fetchItemList({ state, commit, rootState, getters, rootGetters }) {
            commit("bulk/deselectAllForBulkAction", {}, { root: true })
            return $httpX({
                name: "fetchItemList",
                commit,
                url: state.apiSource.endpoint,
                // Not supported in IE11 :-(
                //params: state.queryParamSerializer.getURLSearchParams()
                params: state.apiSource.queryParamSerializer.params,
            })
                .then((response) => {
                    commit("setPagination", _.omit(response.data, "objects"))
                    commit("setItems", response.data.objects)
                    setTimeout(() => applyScrollPos(rootState.route), 25)
                })
                .catch((errors) => {
                    commit("setPagination", null)
                })
        },

        refetchItems({ state, commit, dispatch, getters }, itemIds) {
            return $httpX({
                name: "refetchItems",
                commit,
                url: state.apiSource.endpoint,
                params: {
                    id: itemIds,
                    page_size: 100,
                },
            }).then((response) => {
                for (let item of response.data.objects) {
                    dispatchEvent(EVENTS.itemUpdated, item)
                }
            })
        },

        /***********************
         * Listeners to store events
         ************************/

        ...mapEvents({
            [EVENTS.itemCreated]({ commit }, item) {
                item.added = true
                commit("prependItem", item)
            },

            [EVENTS.itemUpdated]({ commit }, item) {
                commit("updateItemInList", item)
            },

            [EVENTS.itemTrashed]({ commit }, item) {
                commit("removeItemsById", [item.id])
            },

            [EVENTS.itemBulkUpdated]({ dispatch, commit, getters }, { itemIds }) {
                // Don't send API call if we're not on an item list view
                if (!getters.isItemListRoute) {
                    return
                }
                itemIds == "__ALL__" ? dispatch("fetchItemList") : dispatch("refetchItems", itemIds)
            },

            [EVENTS.itemBulkTrashed]({ dispatch, commit, getters }, { itemIds }) {
                // Don't send API call if we're not on an item list view
                if (getters.isItemListRoute && itemIds == "__ALL__") {
                    dispatch("fetchItemList")
                } else if (itemIds != "__ALL__") {
                    commit("removeItemsById", itemIds)
                }
            },

            [EVENTS.itemBulkCopied]({ dispatch, getters }, { itemIds }) {
                // Don't send API call if we're not on an item list view
                if (!getters.isItemListRoute) {
                    return
                }
                dispatch("fetchItemList")
            },

            [EVENTS.itemBulkRemovedFromProjel]({ dispatch, commit }, { itemIds }) {
                commit("removeItemsById", itemIds)
            },
        }),
    },
}
