import _ from "lodash"
import Vue from "vue"
import { $httpX } from "@js/ajax"

export default {
    namespaced: true,
    state: {
        // A map of instance id selected for bulk action : {id: true/false}
        bulkActionSelection: {},
        singleObjectSelection: null,
        wholeListSelected: false,
        wholeListQueryString: {},
    },
    mutations: {
        toggleForBulkAction(state, instance) {
            Vue.set(state.bulkActionSelection, instance.id, !state.bulkActionSelection[instance.id])
            state.wholeListSelected = false
            state.wholeListQueryParams = {}
        },
        selectAllVisiblesForBulkAction(state, instances) {
            for (let instance of instances) {
                Vue.set(state.bulkActionSelection, instance.id, true)
            }
        },
        deselectAllForBulkAction(state) {
            state.bulkActionSelection = {}
            state.wholeListSelected = false
            state.wholeListQueryParams = {}
        },
        setSingleObjectSelection(state, singleId) {
            state.singleObjectSelection = singleId
        },
        selectWholeListForBulkAction(state, queryParams) {
            state.wholeListSelected = true
            state.wholeListQueryParams = queryParams
        },
    },
    getters: {
        bulkActionSelectionAsList(state) {
            return _.map(_.keys(_.pickBy(state.bulkActionSelection)), (id) => parseInt(id))
        },
        anySelectedForBulkAction(state, getters) {
            return getters.bulkActionSelectionAsList.length > 0
        },
    },
    actions: {
        bulkAction({ state, getters, commit, dispatch }, { url, action, params, ids }) {
            if (state.wholeListSelected) {
                ids = "__ALL__"
            } else {
                if (!ids) {
                    ids = state.singleObjectSelection
                        ? [state.singleObjectSelection]
                        : getters.bulkActionSelectionAsList
                }
                ids = _.clone(ids)
            }

            return $httpX({
                name: `bulkAction-${action}`,
                commit,
                url: url,
                method: "POST",
                params: state.wholeListQueryParams,
                data: { action, params, ids },
            }).then(() => {
                commit("deselectAllForBulkAction")
                return ids
            })
        },
    },
}
