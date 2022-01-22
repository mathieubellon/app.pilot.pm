<template>
<div class="bg-white p-5 mx-auto max-w-3xl shadow">
    <ActivityFeed
        class="w-full"
        :inactiveMentionGroups="inactiveMentionGroups"
        namespace="projelDetail"
    />
</div>
</template>
<script>
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"
import ActivityFeed from "@views/activity/ActivityFeed.vue"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "ProjelDetailActivity",
    mixins: [PilotMixin],
    components: {
        ActivityFeed,
    },
    computed: {
        ...mapGetters("projelDetail", ["inactiveMentionGroups"]),
    },
}
</script>
