<template>
<div class="ItemContentForm">
    <ItemContentFormField
        v-for="fieldSchema in contentSchema"
        :fieldSchema="fieldSchema"
        :item="itemEditable"
        :key="fieldSchema.name"
        :validation="validation"
        :warnings="warnings"
        @addElasticElement="onAddElasticElement"
        @annotations="onAnnotations"
        @deleteElasticElement="onDeleteElasticElement"
        @input="onInput"
    />
</div>
</template>

<script>
import { mapState, mapGetters, mapActions, mapMutations } from "vuex"
import realtime from "@js/realtime"

import ItemContentFormField from "@views/items/contentForm/ItemContentFormField"

export default {
    name: "ItemContentForm",
    components: { ItemContentFormField },
    computed: {
        ...mapState("itemContentForm", ["itemEditable", "contentSchema", "validation", "warnings"]),
        isItemContentFrozen() {
            if (!this.$store.state.itemDetail) {
                return false
            }
            return this.$store.state.itemDetail.item.frozen
        },
    },
    methods: {
        ...mapMutations("itemContentForm", ["setItemContentField", "addPendingChange"]),
        ...mapActions("itemContentForm", [
            "saveItemContentRT",
            "addElasticElement",
            "deleteElasticElement",
        ]),

        broadcastChange(change) {
            this.addPendingChange(change)
            this.saveItemContentRT()
        },

        onInput(inputData) {
            if (this.isItemContentFrozen) {
                return
            }
            this.setItemContentField(inputData)
            this.broadcastChange(inputData)
        },

        onAnnotations(annotationsData) {
            if (this.isItemContentFrozen) {
                return
            }
            this.broadcastChange(annotationsData)
        },

        onAddElasticElement({ fieldName, value }) {
            if (this.isItemContentFrozen) {
                return
            }
            this.setItemContentField({ fieldName, value })
            this.broadcastChange({
                fieldName,
                value,
                action: "addElasticElement",
            })
        },

        onDeleteElasticElement({ fieldName, index }) {
            if (this.isItemContentFrozen) {
                return
            }
            //this.deleteElasticElement({fieldName, fieldSchema, index})
            realtime.deleteElasticElement(fieldName, index)
        },
    },
}
</script>
