<template>
<div class="ProjelDetailTasks">
    <h3 class="text-lg font-bold mb-5">{{ $t("tasks") }}</h3>
    <LinkedTasks
        :inactiveMentionGroups="inactiveMentionGroups"
        namespace="projelDetail"
    />
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import LinkedTasks from "@views/tasks/linkedTasks/LinkedTasks.vue"

export default {
    name: "ProjelDetailTasks",
    mixins: [PilotMixin],
    components: {
        LinkedTasks,
    },
    computed: {
        ...mapGetters("projelDetail", ["inactiveMentionGroups"]),
    },
}
</script>
