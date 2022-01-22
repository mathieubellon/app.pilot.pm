<template>
<div class="flex flex-row">
    <span
        v-if="item.project"
        class="mr-5 flex items-center hover:bg-cool-gray-100 hover:text-cool-gray-700 transition transition-colors rounded-md"
        @click="$modal.show('itemDetailSeeProject')"
    >
        <Icon
            class="flex-shrink-0 mr-1 h-4 w-4 text-current text-blue-400"
            name="Project"
        />
        <a
            class="text-cool-gray-500 hover:text-cool-gray-700 flex items-center cursor-pointer"
            @click.prevent
        >
            {{ item.project.name }}
        </a>
    </span>

    <span class="mr-5">#{{ item.id }}</span>

    <!-- <span class="mr-3 flex items-center">
            <ItemTypeIcon
                class="flex-shrink-0 mr-1 h-4 w-4 text-blue-400"
                :name="item.item_type.icon_name"
            />

            <span class="mr-2">{{ item.item_type.name }}</span>
        </span> -->
    <span
        class="flex items-center hover:bg-cool-gray-100 hover:text-cool-gray-700 transition transition-colors rounded-md"
    >
        <Icon
            class="flex-shrink-0 mr-1 h-4 w-4 text-green-400"
            name="CheckCircleHeroicon"
        />
        <ItemRealtimeState />
    </span>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import ItemRealtimeState from "@views/items/detail/header/ItemRealtimeState.vue"

export default {
    name: "ItemDetailTopBarSubtitle",
    mixins: [PilotMixin],
    components: {
        ItemRealtimeState,
    },
    computed: {
        ...mapState("itemDetail", ["item"]),
    },
}
</script>
