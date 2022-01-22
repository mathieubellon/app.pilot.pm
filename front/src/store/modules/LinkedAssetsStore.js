import _ from "lodash"
import axios from "axios"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import { getFileProperties } from "@js/assetsUtils"

export default {
    namespaced: true,
    state: () => ({
        linkedAssets: [],
        contentType: null,
        objectId: null,

        isAssetUrlFormVisible: false,
        zipStep: "ready",
        refreshZipUrl: null,
        zipUrl: null,
    }),
    mutations: {
        initLinkedAssetsStore(state, { contentType, objectId }) {
            state.contentType = contentType
            state.objectId = objectId
        },
        setLinkedAssets(state, linkedAssets) {
            state.linkedAssets = linkedAssets
        },
        prependLinkedAsset(state, linkedAsset) {
            state.linkedAssets.unshift(linkedAsset)
        },
        removeLinkedAsset(state, linkedAsset) {
            state.linkedAssets = state.linkedAssets.filter((asset) => asset.id != linkedAsset.id)
        },
        updateLinkedAsset(state, linkedAsset) {
            state.linkedAssets = state.linkedAssets.map((oldAsset) =>
                oldAsset.id == linkedAsset.id ? linkedAsset : oldAsset,
            )
        },
        showAssetUrlForm(state) {
            state.isAssetUrlFormVisible = true
        },
        hideAssetUrlForm(state) {
            state.isAssetUrlFormVisible = false
        },
        setZipStep(state, zipStep) {
            state.zipStep = zipStep
        },
        setRefreshZipUrl(state, refreshZipUrl) {
            state.refreshZipUrl = refreshZipUrl
        },
        setZipUrl(state, zipUrl) {
            state.zipUrl = zipUrl
        },
    },
    getters: {
        isAssetLinked: (state) => (assetId) => {
            return _.some(state.linkedAssets, (asset) => asset.id == assetId)
        },
    },
    actions: {
        fetchLinkedAssets({ state, commit }) {
            $httpX({
                name: "fetchLinkedAssets",
                commit,
                url: urls.assetsLinked.format({
                    contentTypeId: state.contentType.id,
                    objectId: state.objectId,
                }),
            }).then((response) => {
                commit("setLinkedAssets", response.data)
            })
        },
        addUploadedAsset({ state, commit }, file) {
            let assetData = getFileProperties(file)
            _.assign(assetData, {
                assetId: file.assetId,
                content_type_id: state.contentType ? state.contentType.id : null,
                object_id: state.objectId,
                in_media_library: false,
            })

            return $httpX({
                name: "addUploadedAsset",
                commit,
                url: urls.assets,
                method: "POST",
                data: assetData,
            }).then((response) => {
                let asset = response.data
                commit("prependLinkedAsset", asset)
                return asset
            })
        },
        partialUpdateAsset({ commit }, assetData) {
            return $httpX({
                name: "partialUpdateAsset" + assetData.id,
                commit,
                url: urls.assets.format({ id: assetData.id }),
                method: "PATCH",
                data: assetData,
            }).then((response) => {
                commit("updateLinkedAsset", response.data)
            })
        },
        linkAsset({ state, commit, getters }, asset) {
            if (getters.isAssetLinked(asset.id)) return

            $httpX({
                name: `linkAsset-${asset.id}`,
                commit,
                url: urls.assetsLink.format({ id: asset.id }),
                method: "POST",
                data: {
                    content_type_id: state.contentType.id,
                    object_id: state.objectId,
                },
            }).then((response) => {
                commit("prependLinkedAsset", asset)
            })
        },
        unlinkAsset({ state, commit, getters }, asset) {
            if (!getters.isAssetLinked(asset.id)) return

            $httpX({
                name: "unlinkAsset",
                commit,
                url: urls.assetsUnlink.format({ id: asset.id }),
                method: "POST",
                data: {
                    content_type_id: state.contentType.id,
                    object_id: state.objectId,
                },
            }).then((response) => {
                // Insert the linked asset at the beggining of the list
                commit("removeLinkedAsset", asset)
            })
        },
        deleteAsset({ state, commit }, asset) {
            $httpX({
                name: "deleteAsset",
                commit,
                url: urls.assets.format({ id: asset.id }),
                method: "DELETE",
                data: {
                    content_type_id: state.contentType.id,
                    object_id: state.objectId,
                },
            }).then((response) => {
                // Remove the asset from the list
                commit("removeLinkedAsset", asset)
            })
        },

        requestAssetsZip({ state, commit, dispatch }) {
            if (state.zipStep != "ready" || state.linkedAssets.length == 0) {
                return
            }
            commit("setZipStep", "requested")

            $httpX({
                name: "downloadZip",
                commit,
                url: urls.assetsStartZip,
                data: {
                    content_type_id: state.contentType.id,
                    object_id: state.objectId,
                },
                method: "POST",
            }).then((response) => {
                if (response.data.assembly_ssl_url) {
                    commit("setRefreshZipUrl", response.data.assembly_ssl_url)
                    dispatch("refreshZipLink")
                } else {
                    commit("setZipStep", "error")
                }
            })
        },
        refreshZipLink({ state, commit, dispatch }) {
            if (state.zipUrl) {
                return
            }

            // Use axios directly instead of $http,
            // to avoid sending the X-CSRFToken header to transloadit
            axios.get(state.refreshZipUrl).then((response) => {
                if (response.data.ok == "ASSEMBLY_COMPLETED") {
                    commit("setZipStep", "generated")
                    commit("setZipUrl", response.data.results.concat[0].url)
                } else if (response.data.error) {
                    commit("setZipStep", "error")
                } else {
                    setTimeout(() => dispatch("refreshZipLink"), 3000)
                }
            })
        },
    },
}
