<template>
<Fragment>
    <!-- The span is required to prevent Vue error with component reuse -->
    <span v-if="!item.in_trash">
        <ItemStateDropdown
            :inactiveMentionGroups="inactiveMentionGroups"
            :item="item"
            :showStateText="true"
            @saved="onStateSaved"
        />
    </span>

    <!-- The span is required to prevent Vue error with component reuse -->
    <span v-if="!item.in_trash">
        <ItemTableOfContents />
    </span>

    <ItemTrashedState />

    <!-- The span is required to prevent Vue error with component reuse -->
    <span v-if="!item.in_trash">
        <Popper
            position="auto"
            triggerElementName="PopperRef"
            triggerType="click"
        >
            <template #triggerElement>
                <button
                    class="button is-topbar"
                    :class="{
                        'bg-yellow-300 text-yellow-800': item.frozen,
                        'bg-red-800 text-red-100': isPrivateItem,
                    }"
                    ref="PopperRef"
                    type="button"
                >
                    {{ $t("actions") }}
                    <!-- The empty span is required to correctly align with flex display -->
                    <span>
                        <Icon
                            class="caret"
                            name="ChevronDown"
                        />
                    </span>
                </button>
            </template>

            <template #content>
                <ItemDetailOptions />
            </template>
        </Popper>
    </span>
</Fragment>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"
import { Fragment } from "vue-fragment"

import ItemStateDropdown from "@views/items/ItemStateDropdown.vue"
import ItemTrashedState from "@views/items/detail/header/ItemTrashedState.vue"
import ItemDetailOptions from "@views/items/detail/header/ItemDetailOptions.vue"
import ItemTableOfContents from "@views/items/detail/header/ItemTableOfContents.vue"

export default {
    name: "ItemDetailTopBarActions",
    mixins: [PilotMixin],
    components: {
        Fragment,
        ItemDetailOptions,
        ItemStateDropdown,
        ItemTrashedState,
        ItemTableOfContents,
    },
    computed: {
        ...mapState("itemDetail", ["item", "inactiveMentionGroups"]),
        isPrivateItem() {
            return this.currentDesk.privateItemsEnabled && this.item.is_private
        },
    },
    methods: {
        ...mapActions("itemDetail", ["receiveItem"]),
        ...mapActions("itemDetail/activityFeed", ["fetchActivities"]),
        onStateSaved(item) {
            // Update the item with the new state
            this.receiveItem(item)
            // Reload the activity list
            this.fetchActivities()
        },
    },
}
</script>
