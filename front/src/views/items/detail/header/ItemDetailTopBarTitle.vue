<template>
<div class="flex items-center">
    <ItemTypeIcon
        class="flex-shrink-0 mr-1 h-4 w-4 text-blue-400"
        :name="item.item_type.icon_name"
    />
    <span class="truncate">
        {{ itemEditable.content.title ? itemEditable.content.title : $t("untitled") }}
    </span>

    <div
        v-if="currentRealtimeState == REALTIME_STATES.conflict"
        class="button bg-purple-400 cursor-default"
    >
        {{ $t("conflict") }}
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"
import ItemTypeIcon from "@views/itemTypes/ItemTypeIcon"
import { REALTIME_STATES } from "@/store/modules/ItemContentFormStore.js"

export default {
    name: "ItemDetailTopBarTitle",
    mixins: [PilotMixin],
    components: {
        ItemTypeIcon,
    },
    data: () => ({
        REALTIME_STATES,
    }),
    computed: {
        ...mapState("itemDetail", ["item"]),
        ...mapState("itemContentForm", ["itemEditable"]),
        ...mapGetters("itemContentForm", ["currentRealtimeState"]),
    },
}
</script>
