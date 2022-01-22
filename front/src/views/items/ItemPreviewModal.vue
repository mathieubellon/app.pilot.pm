<template>
<Modal
    name="itemPreview"
    height="auto"
    :pivotY="0.1"
    :scrollable="true"
    @close="setItemPreviewed(null)"
>
    <div class="p-8">
        <div class="Item__metadata">
            <div class="font-semibold text-gray-900 mb-1">ID</div>
            #{{ itemPreviewed.id }}
        </div>
        <div
            v-if="currentDesk.itemLanguagesEnabled"
            class="Item__metadata"
        >
            <div class="font-semibold text-gray-900 mb-1">{{ $t("language") }}</div>
            {{ itemPreviewed.language | defaultVal("-") }}
        </div>
        <div
            v-if="itemPreviewed.item_type"
            class="Item__metadata"
        >
            <div class="font-semibold text-gray-900 mb-1">Type</div>
            {{ itemPreviewed.item_type.name }}
        </div>
        <div class="Item__metadata">
            <div class="font-semibold text-gray-900 mb-1">{{ $t("createdBy") }}</div>
            <UserDisplay :user="itemPreviewed.created_by" />
            &nbsp;{{ $t("at") }} {{ itemPreviewed.created_at | dateFormat }}
        </div>
        <div class="bg-gray-50 p-2 rounded">
            <Loadarium name="fetchItemContent">
                <ItemContentReadOnly :itemReadOnly="itemReadOnly" />
            </Loadarium>
        </div>
    </div>
</Modal>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { ItemReadOnly } from "@js/items/ItemReadOnly"
import PilotMixin from "@components/PilotMixin"

import ItemContentReadOnly from "@views/items/contentForm/ItemContentReadOnly"

export default {
    name: "ItemPreviewModal",
    mixins: [PilotMixin],
    components: {
        ItemContentReadOnly,
    },
    computed: {
        ...mapState("itemActions", ["itemPreviewed"]),
        itemReadOnly() {
            return ItemReadOnly.fromItem(this.itemPreviewed)
        },
    },
    methods: {
        ...mapMutations("itemActions", ["setItemPreviewed"]),
    },
}
</script>
