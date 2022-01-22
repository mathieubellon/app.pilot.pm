<template>
<MainLayout>
    <template #title>
        <AssetDetailTopbar v-if="asset.id" />
        <!-- Initial Asset Loading -->
        <span v-else>{{ $t("loading") }}</span>
    </template>

    <template #actions>
        <AssetDetailTopBarActions v-if="asset.id" />
    </template>

    <template #middlebar>
        <AssetDetailTabs />
    </template>

    <template #content>
        <router-view class="p-2 md:p-8 md:pr-4" />
    </template>
</MainLayout>
</template>

<script>
import { mapState, mapMutations, mapActions } from "vuex"

import PilotMixin from "@components/PilotMixin"

import MainLayout from "@components/layout/MainLayout"

import AssetDetailTopbar from "./AssetDetailTopbar"
import AssetDetailTabs from "./AssetDetailTabs"
import AssetDetailTopBarActions from "./AssetDetailTopBarActions"

export default {
    name: "AssetDetailApp",
    mixins: [PilotMixin],
    components: {
        MainLayout,

        AssetDetailTopbar,
        AssetDetailTopBarActions,
        AssetDetailTabs,
    },
    computed: {
        ...mapState("assetDetail", ["asset", "assetConverter"]),
    },
    methods: {
        ...mapMutations("assetDetail", ["setAsset"]),
        ...mapActions("assetDetail", ["fetchAsset"]),
        init() {
            this.assetConverter.on("conversionStatusUpdate", (asset) => {
                this.setAsset(asset)
            })

            this.fetchAsset()
        },
    },
    created() {
        this.init()
    },
    beforeRouteUpdate(to, from, next) {
        // We're changing the asset id, we must fetch it from the API
        if (to.params.id != from.params.id) {
            this.$nextTick(this.init)
        }
        next()
    },
}
</script>
