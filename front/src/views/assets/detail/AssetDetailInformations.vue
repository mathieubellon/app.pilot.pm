<template>
<div class="AssetDetailInformations">
    <div
        v-if="viewportPhone"
        class="flex flex-col"
    >
        <AssetDetailPreview />
        <AssetDetailDescription />
        <AssetDetailSideBar />
    </div>
    <div
        v-else
        class="flex"
    >
        <div class="w-1/3 mr-6">
            <AssetDetailSideBar />
        </div>

        <div class="flex flex-col w-2/3 max-w-screen-md">
            <AssetDetailDescription />
            <AssetDetailPreview />
        </div>
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"
import ResponsiveMixin from "@components/ResponsiveMixin"

import AssetDetailSideBar from "./AssetDetailSideBar"
import AssetDetailDescription from "./AssetDetailDescription"
import AssetDetailPreview from "./AssetDetailPreview"

export default {
    name: "AssetDetailInformations",
    mixins: [PilotMixin, ResponsiveMixin],
    components: {
        AssetDetailSideBar,
        AssetDetailDescription,
        AssetDetailPreview,
    },
    computed: {
        ...mapState("assetDetail", ["asset"]),
    },
}
</script>
