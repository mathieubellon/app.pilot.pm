<template>
<div class="ItemContentReadOnly">
    <div
        v-for="fieldSchema in allFieldSchemas"
        class="mb-8"
    >
        <div class="form__field__label">
            {{ fieldSchema.label }}
        </div>

        <ItemContentFieldReadOnly
            class="text-gray-800 mb-4 bg-transparent"
            :annotations="itemReadOnly.annotations"
            :fieldSchema="fieldSchema"
            :value="itemReadOnly.content[fieldSchema.name]"
        />
    </div>
</div>
</template>

<script>
import ItemContentFieldReadOnly from "./ItemContentFieldReadOnly.vue"
import PilotMixin from "@components/PilotMixin"

import { getAllFieldSchemas } from "@js/items/itemsUtils"

export default {
    name: "ItemContentReadOnly",
    mixins: [PilotMixin],
    components: {
        ItemContentFieldReadOnly,
    },
    props: {
        itemReadOnly: Object,
    },
    computed: {
        allFieldSchemas() {
            return getAllFieldSchemas(this.itemReadOnly.contentSchema, this.itemReadOnly.content)
        },
    },
}
</script>
