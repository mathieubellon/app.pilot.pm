<template>
<div class="ItemDrawer">
    <div class="ItemDrawer__Header">
        {{ $t("comments") }}

        <div
            class="ItemDrawer__Header__Close"
            @click="closePanel()"
        >
            {{ $t("close") }}
        </div>
    </div>
    <ActivityFeed
        :inactiveMentionGroups="inactiveMentionGroups"
        namespace="itemDetail"
    />
</div>
</template>

<script>
import { mapActions, mapGetters } from "vuex"
import PilotMixin from "@components/PilotMixin"

import ActivityFeed from "@views/activity/ActivityFeed.vue"

export default {
    name: "DrawerActivity",
    mixins: [PilotMixin],
    components: { ActivityFeed },
    computed: {
        ...mapGetters("itemDetail", ["inactiveMentionGroups"]),
    },
    methods: {
        ...mapActions("itemDetail", ["closePanel"]),
    },
}
</script>
