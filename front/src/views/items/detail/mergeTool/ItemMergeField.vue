<template>
<div class="ItemMergeField">
    <div class="ItemContentMergeTool__panels">
        <div class="ItemContentMergeTool__panel w-2/5">
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

        <div class="ItemContentMergeTool__panel ml-2 w-2/5">
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
                :value="result"
            />
        </div>

        <div class="ItemContentMergeTool__panel ml-2 w-1/5">
            <template v-if="hasChanged">
                <button
                    v-if="accepted"
                    class="button is-indigo"
                    @click="reject"
                >
                    {{ $t("rejectChange") }}
                </button>
                <button
                    v-else
                    class="button is-teal"
                    @click="accept"
                >
                    {{ $t("acceptChange") }}
                </button>
            </template>
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
    name: "ItemMergeField",
    mixins: [PilotMixin],
    components: { ItemContentFieldReadOnly },
    props: {
        fieldSchema: Object,
    },
    data: () => ({
        accepted: true,
    }),
    computed: {
        ...mapState("itemDetail", ["editSessionForMergeTool"]),
        ...mapState("itemContentForm", ["itemEditable"]),
        fieldName() {
            return this.fieldSchema.name
        },
        oldValue() {
            return this.editSessionForMergeTool.content[this.fieldName]
        },
        newValue() {
            return this.itemEditable.content[this.fieldName]
        },
        result() {
            return this.accepted ? this.newValue : this.oldValue
        },
        hasChanged() {
            return !_.isEqual(this.oldValue, this.newValue)
        },
        hasDiff() {
            return !_.isEqual(this.oldValue, this.result)
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
    methods: {
        accept() {
            this.accepted = true
            this.emitChange()
        },
        reject() {
            this.accepted = false
            this.emitChange()
        },
        emitChange() {
            this.$emit("mergeChange", {
                fieldName: this.fieldName,
                value: this.result,
            })
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
