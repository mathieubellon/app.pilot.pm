<template>
<div class="ItemDrawer DrawerAssets">
    <div class="ItemDrawer__Header">
        {{ $t("linkedAssets") }}

        <div
            class="ItemDrawer__Header__Close"
            @click="closePanel()"
        >
            {{ $t("close") }}
        </div>
    </div>

    <LinkedAssets namespace="itemDetail" />
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import LinkedAssets from "@views/assets/linked/LinkedAssets.vue"

export default {
    name: "DrawerAssets",
    mixins: [PilotMixin],
    components: {
        LinkedAssets,
    },
    methods: {
        ...mapActions("itemDetail", ["closePanel"]),
    },
}
</script>
