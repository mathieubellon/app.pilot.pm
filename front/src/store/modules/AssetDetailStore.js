import _ from "lodash"
import Vue from "vue"
import urls from "@js/urls"
import { $httpX } from "@js/ajax"

import AssetConverter from "@js/AssetConverter"
import { EVENTS, mapEvents, dispatchEvent } from "@js/events"

export default {
    namespaced: true,
    state: {
        asset: {},
        // Keep track of fields that are currently being saved
        // {fieldName : true/false}
        fieldsCurrentlyUpdating: {},
        isTitleInEdition: false,
        isUploadingFile: false,
        assetConverter: new AssetConverter(),
    },
    mutations: {
        setAsset(state, asset) {
            state.asset = asset
            // If an assembly is executing, start to poll for the conversion status
            if (asset.is_assembly_executing) {
                state.assetConverter.waitForAssetConversionStatus(asset)
            }
        },
        startFieldsCurrentlyUpdating(state, fields) {
            for (let fieldName in fields) {
                Vue.set(state.fieldsCurrentlyUpdating, fieldName, true)
            }
        },
        stopFieldsCurrentlyUpdating(state, fields) {
            for (let fieldName in fields) {
                Vue.set(state.fieldsCurrentlyUpdating, fieldName, false)
            }
        },
        setIsTitleInEdition(state, isTitleInEdition) {
            state.isTitleInEdition = isTitleInEdition
        },
        setIsUploadingFile(state, isUploadingFile) {
            state.isUploadingFile = isUploadingFile
        },
        updateLabel(state, label) {
            if (state.asset && state.asset.folder && state.asset.folder.id == label.id) {
                state.asset.folder = label
            }
        },
        removeLabel(state, label) {
            if (state.asset && state.asset.folder && state.asset.folder.id == label.id) {
                state.asset.folder = null
            }
        },
    },
    getters: {
        assetId(state, getters, rootState) {
            return parseInt(rootState.route.params.id)
        },
    },
    actions: {
        fetchAsset({ getters, commit }) {
            commit("setAsset", {})
            return $httpX({
                commit,
                name: "fetchAsset",
                method: "GET",
                url: urls.assets.format({ id: getters.assetId }),
                handle404: true,
            }).then((response) => {
                commit("setAsset", response.data)
            })
        },

        partialUpdateAsset({ state, commit }, assetData) {
            commit("startFieldsCurrentlyUpdating", assetData)
            return $httpX({
                name: "partialUpdateAsset",
                commit,
                method: "PATCH",
                url: urls.assets.format({ id: state.asset.id }),
                data: assetData,
            })
                .then((response) => {
                    let asset = response.data
                    commit("setAsset", asset)
                    dispatchEvent(EVENTS.assetUpdated, asset)
                })
                .finally(() => {
                    commit("stopFieldsCurrentlyUpdating", assetData)
                })
        },

        deleteAsset({ state, commit }) {
            $httpX({
                name: "deleteAsset",
                commit,
                method: "DELETE",
                url: urls.assets.format({ id: state.asset.id }),
            }).then((response) => {
                dispatchEvent(EVENTS.assetDeleted, response.data)
            })
        },

        deleteAssetRight({ state, commit }, assetRight) {
            $httpX({
                name: "deleteAssetRight",
                commit,
                method: "DELETE",
                url: urls.assetRights.format({ id: assetRight.id }),
            }).then((response) => {
                let asset = _.cloneDeep(state.asset)
                asset.asset_rights = asset.asset_rights.filter((ar) => ar.id != assetRight.id)
                commit("setAsset", asset)
            })
        },

        /***********************
         * Listeners to store events
         ************************/

        ...mapEvents({
            [EVENTS.labelUpdated]({ commit }, label) {
                commit("updateLabel", label)
            },

            [EVENTS.labelDeleted]({ commit }, label) {
                commit("removeLabel", label)
            },
        }),
    },
}
