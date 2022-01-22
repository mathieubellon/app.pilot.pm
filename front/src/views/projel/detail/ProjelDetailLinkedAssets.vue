<template>
<LinkedAssets namespace="projelDetail" />
</template>
<script>
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"
import LinkedAssets from "@views/assets/linked/LinkedAssets.vue"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "ProjelDetailLinkedAssets",
    mixins: [PilotMixin],
    components: {
        LinkedAssets,
    },
}
</script>
