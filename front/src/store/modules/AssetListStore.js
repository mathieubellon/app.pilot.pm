import _ from "lodash"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import { EVENTS, mapEvents, dispatchEvent } from "@js/events"
import { applyScrollPos } from "@js/bootstrap"
import { getFileProperties } from "@js/assetsUtils"

export default {
    namespaced: true,
    state: () => ({
        apiSource: null,
        assets: [],
        pagination: null,
        savedQuery: null,
    }),
    mutations: {
        setApiSource(state, apiSource) {
            state.apiSource = apiSource
        },
        setAssets(state, assets) {
            state.assets = assets
        },
        prependAsset(state, asset) {
            state.assets.unshift(asset)
        },
        updateAsset(state, asset) {
            state.assets = state.assets.map((oldAsset) =>
                oldAsset.id == asset.id ? asset : oldAsset,
            )
        },
        setPagination(state, pagination) {
            state.pagination = pagination
        },
        saveQuery(state, query) {
            state.savedQuery = query
        },
    },
    actions: {
        fetchAssetList({ state, commit, rootState }) {
            return $httpX({
                name: "fetchAssetList",
                commit,
                url: state.apiSource.endpoint,
                // Not supported in IE11 :-(
                //params: state.queryParamSerializer.getURLSearchParams()
                params: state.apiSource.queryParamSerializer.params,
            })
                .then((response) => {
                    commit("setPagination", _.omit(response.data, "objects"))
                    commit("setAssets", response.data.objects)
                    setTimeout(() => applyScrollPos(rootState.route), 25)
                })
                .catch((errors) => {
                    commit("setPagination", null)
                })
        },

        addUploadedAsset({ state, commit }, file) {
            let assetData = getFileProperties(file)

            _.assign(assetData, {
                assetId: file.assetId,
                in_media_library: true,
            })

            return $httpX({
                name: "addUploadedAsset",
                commit,
                url: urls.assets,
                method: "POST",
                data: assetData,
            }).then((response) => {
                let asset = response.data
                dispatchEvent(EVENTS.assetCreated, asset)
                return asset
            })
        },

        /***********************
         * Listeners to store events
         ************************/

        ...mapEvents({
            [EVENTS.assetCreated]({ commit }, asset) {
                commit("prependAsset", asset)
            },
        }),
    },
}
