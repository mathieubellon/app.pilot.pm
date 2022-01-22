<template>
<div class="ItemContentDiffField">
    <div class="ItemContentDiff__panels">
        <div class="ItemContentDiff__panel w-1/4">
            <div
                v-if="hasDiff && !oldValue"
                class="InputStyling bg-gray-300 text-center"
            >
                ∅
            </div>

            <div
                v-else-if="hasTextualDiff"
                class="InputStyling bg-red-100"
            >
                <div v-html="oldTextDiff" />
            </div>

            <ItemContentFieldReadOnly
                v-else
                :class="{
                    'bg-red-100': hasDiff,
                    'text-gray-500': !hasDiff,
                }"
                :fieldSchema="fieldSchema"
                :value="oldValue"
            />
        </div>

        <div class="ItemContentDiff__panel ml-2 w-1/4">
            <div
                v-if="hasDiff && !newValue"
                class="InputStyling bg-gray-300 text-center"
            >
                ∅
            </div>

            <div
                v-else-if="hasTextualDiff"
                class="InputStyling bg-green-100"
            >
                <div v-html="newTextDiff" />
            </div>

            <ItemContentFieldReadOnly
                v-else
                :class="{
                    'bg-green-100': hasDiff,
                    'text-gray-500': !hasDiff,
                }"
                :fieldSchema="fieldSchema"
                :value="newValue"
            />
        </div>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { formatDiff, textDiff } from "@js/diff/textDiff"

import PilotMixin from "@components/PilotMixin"
import ItemContentFieldReadOnly from "@views/items/contentForm/ItemContentFieldReadOnly"

export default {
    name: "ItemContentDiffField",
    mixins: [PilotMixin],
    components: { ItemContentFieldReadOnly },
    props: {
        fieldSchema: Object,
        itemReadOnly: Object,
    },
    computed: {
        fieldName() {
            return this.fieldSchema.name
        },
        fieldDiff() {
            let diff = this.itemReadOnly.fieldDiffs[this.fieldName]
            return diff || {}
        },
        oldValue() {
            return this.fieldDiff.old_value
        },
        newValue() {
            return this.fieldDiff.new_value
        },
        hasDiff() {
            return !_.isEqual(this.oldValue, this.newValue)
        },
        hasTextualDiff() {
            return (
                this.hasDiff && (this.fieldSchema.type == "text" || this.fieldSchema.type == "char")
            )
        },
        textDiff() {
            return textDiff(this.oldValue, this.newValue)
        },
        oldTextDiff() {
            return formatDiff(this.textDiff, { withInsertions: false })
        },
        newTextDiff() {
            return formatDiff(this.textDiff, { withDeletion: false })
        },
    },
    i18n: {
        messages: {
            fr: {
                acceptChange: "Conserver cette modification",
                noDifference: "Aucune différence",
                rejectChange: "Rejeter cette modification",
            },
            en: {
                acceptChange: "Accept this change",
                noDifference: "No difference",
                rejectChange: "Reject this change",
            },
        },
    },
}
</script>
