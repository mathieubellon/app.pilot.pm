<template>
<div class="px-8">
    <FullCalendar v-if="sharing.type == SharingType.CALENDAR" />

    <ItemList
        v-else
        class="py-4"
        context="shared"
    />
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"
import { SharingType } from "@/store/PublicSharingStore"

import ItemList from "@views/items/list/ItemList"
import FullCalendar from "@views/items/calendar/FullCalendar.vue"

export default {
    name: "Sharing",
    mixins: [PilotMixin],
    components: {
        ItemList,
        FullCalendar,
    },
    data: () => ({
        SharingType,
    }),
    computed: {
        ...mapState(["sharing"]),
    },
}
</script>
