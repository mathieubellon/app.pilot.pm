import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import { EVENTS, dispatchEvent } from "@js/events"
import { mainApp } from "@js/bootstrap"

export default {
    namespaced: true,
    state: () => ({
        itemPreviewed: {},
    }),
    mutations: {
        setItemPreviewed(state, item) {
            state.itemPreviewed = item
        },
    },
    actions: {
        fetchItemContent({ state, commit, dispatch }, itemId) {
            return $httpX({
                name: `fetchItemContent`,
                commit,
                method: "GET",
                url: urls.items.format({ id: itemId }),
            }).then((response) => {
                dispatchEvent(EVENTS.itemUpdated, response.data)
                return response.data
            })
        },
        bulkUpdateItems({ state, commit, dispatch }, updateData) {
            return dispatch(
                "bulk/bulkAction",
                {
                    url: urls.itemsBulkAction,
                    action: "update",
                    params: updateData,
                },
                { root: true },
            ).then((itemIds) => {
                dispatchEvent(EVENTS.itemBulkUpdated, { itemIds })
            })
        },
        bulkTrashItems({ state, commit, dispatch }, itemIds) {
            return dispatch(
                "bulk/bulkAction",
                {
                    url: urls.itemsBulkAction,
                    action: "trash",
                    ids: itemIds,
                },
                { root: true },
            ).then((itemIds) => {
                dispatchEvent(EVENTS.itemBulkTrashed, { itemIds })
            })
        },
        bulkCopyItems({ state, dispatch }, itemIds) {
            return dispatch(
                "bulk/bulkAction",
                {
                    url: urls.itemsBulkAction,
                    action: "copy",
                    ids: itemIds,
                },
                { root: true },
            ).then(() => {
                dispatchEvent(EVENTS.itemBulkCopied, { itemIds })
            })
        },
        removeItemsFromProjel({ state, commit, dispatch, rootGetters }, { projelId, itemIds }) {
            let url = rootGetters["projelDetail/isChannelRoute"]
                ? urls.channelsRemoveItems
                : urls.projectsRemoveItems
            return $httpX({
                name: `removeItemsFromProjel`,
                commit,
                method: "PUT",
                url: url.format({ id: projelId }),
                data: { itemIds },
            }).then((response) => {
                commit("bulk/deselectAllForBulkAction", {}, { root: true })
                dispatchEvent(EVENTS.itemBulkRemovedFromProjel, { projelId, itemIds })
            })
        },
        showItemPreviewModal({ state, commit, dispatch }, item) {
            commit("setItemPreviewed", item)
            dispatch("fetchItemContent", item.id).then((item) => {
                commit("setItemPreviewed", item)
            })
            mainApp.$modal.show(`itemPreview`)
        },
        updateItemPublicationDate({ state, commit, dispatch }, itemData) {
            return $httpX({
                name: `updateItemPublicationDate${itemData.id}`,
                commit,
                method: "PATCH",
                url: urls.items.format({ id: itemData.id }),
                data: itemData,
            }).then((response) => {
                dispatchEvent(EVENTS.itemUpdated, response.data)
            })
        },
    },
}
