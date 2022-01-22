<template>
<div class="ItemDrawer DrawerTasks">
    <div class="ItemDrawer__Header">
        {{ $t("tasks") }}

        <div
            class="ItemDrawer__Header__Close"
            @click="closePanel()"
        >
            {{ $t("close") }}
        </div>
    </div>
    <LinkedTasks
        :inactiveMentionGroups="inactiveMentionGroups"
        :isItemTask="true"
        namespace="itemDetail"
    />
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import LinkedTasks from "@views/tasks/linkedTasks/LinkedTasks.vue"

export default {
    name: "DrawerTasks",
    mixins: [PilotMixin],
    components: {
        LinkedTasks,
    },
    computed: {
        ...mapState("itemDetail", ["item"]),
        ...mapGetters("itemDetail", ["itemId", "inactiveMentionGroups"]),
    },
    methods: {
        ...mapActions("itemDetail", ["closePanel"]),
    },
}
</script>
