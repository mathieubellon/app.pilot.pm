<script>
import {
    mapInstanceState,
    mapInstanceGetters,
    mapInstanceMutations,
    mapInstanceActions,
} from "@js/lib/vuex-helpers"

const getNamespace = (vm) => `${vm.namespace}/linkedAssets`

export default {
    name: "LinkedAssetsStoreMapper",
    props: {
        namespace: String,
    },
    computed: {
        ...mapInstanceState(getNamespace, [
            "linkedAssets",
            "contentType",
            "objectId",
            "isAssetUrlFormVisible",
            "zipStep",
            "refreshZipUrl",
            "zipUrl",
        ]),
        ...mapInstanceGetters(getNamespace, ["isAssetLinked"]),
    },
    methods: {
        ...mapInstanceMutations(getNamespace, [
            "initLinkedAssetsStore",
            "setLinkedAssets",
            "prependLinkedAsset",
            "removeLinkedAsset",
            "updateLinkedAsset",
            "showAssetUrlForm",
            "hideAssetUrlForm",
            "setZipStep",
            "setRefreshZipUrl",
            "setZipUrl",
        ]),
        ...mapInstanceActions(getNamespace, [
            "fetchLinkedAssets",
            "addUploadedAsset",
            "partialUpdateAsset",
            "linkAsset",
            "unlinkAsset",
            "deleteAsset",
            "requestAssetsZip",
            "refreshZipLink",
        ]),
    },
}
</script>
