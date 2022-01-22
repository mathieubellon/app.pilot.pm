import urls from "@js/urls"
import { $httpX } from "@js/ajax"

import { ItemReadOnly } from "@js/items/ItemReadOnly"

export default {
    namespaced: true,
    state: {
        // The main item resource we're viewing
        item: {},
        // An ItemReadOnly instance for the item content currently displayed  (content + annotation + version)
        itemReadOnly: new ItemReadOnly({}),
    },
    mutations: {
        setItem(state, item) {
            state.item = item
            if (item.id) {
                state.itemReadOnly = ItemReadOnly.fromItem(item)
            }
        },
    },
    getters: {
        itemId(state, getters, rootState) {
            return rootState.route.params.itemId
        },
        sharedItemUrl(state, getters, rootState) {
            return urls.sharedItem.format({
                token: rootState.sharing.token,
                itemId: getters.itemId,
            })
        },
        feedback(state, getters, rootState, rootGetters) {
            return rootGetters.feedbacks[getters.itemId]
        },
    },
    actions: {
        fetchSharedItem({ state, getters, commit, dispatch }) {
            commit("setItem", {})
            commit("itemContentForm/reset", null, { root: true })

            $httpX({
                name: "fetchSharedItem",
                commit,
                url: getters.sharedItemUrl,
            }).then((response) => {
                let item = response.data
                commit("setItem", item)
                commit("itemContentForm/setItem", item, { root: true })
            })
        },
        createItemFeedback(
            { state, getters, commit, dispatch, rootState },
            { status, feedbackMessage },
        ) {
            return $httpX({
                name: "createItemFeedback",
                commit,
                url: urls.sharedItemFeedback.format({ token: rootState.sharing.token }),
                method: "POST",
                data: {
                    item_id: getters.itemId,
                    status: status,
                    feedback_message: feedbackMessage,
                },
            }).then((response) => {
                commit("appendFeedback", response.data, { root: true })
            })
        },
    },
}
