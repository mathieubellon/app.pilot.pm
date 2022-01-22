import _ from "lodash"

import ItemListStore from "./modules/ItemListStore"
import ItemCalendarStore from "./modules/ItemCalendarStore"
import ItemContentFormStore from "./modules/ItemContentFormStore"
import SharedItemStore from "./modules/SharedItemStore"

export const SharingType = {
    ITEM: "item",
    PROJECT: "project",
    CHANNEL: "channel",
    LIST: "list",
    CALENDAR: "calendar",
}

export default {
    modules: {
        itemList: ItemListStore,
        calendar: ItemCalendarStore,
        itemContentForm: ItemContentFormStore,
        sharedItem: SharedItemStore,
    },
    state: {
        // Sharing resource
        sharing: {},
    },
    mutations: {
        setSharing(state, sharing) {
            state.sharing = sharing
        },
        appendFeedback(state, feedback) {
            state.sharing.feedbacks.push(feedback)
        },
    },
    getters: {
        feedbacks(state) {
            return _.keyBy(state.sharing.feedbacks, "item_id")
        },
    },
    actions: {
        /*
        fetchSharing({state, getters, commit, dispatch}){
            $httpX({
                name: 'fetchSharing',
                commit,
                url: urls.sharings.format({token: state.sharing.token})
            })
            .then(response => {
                let sharing = response.data
                commit('setSharing', sharing)
            })
        }
        */
    },
}
