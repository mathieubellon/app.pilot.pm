<template>
<div class="ItemContentDiffProsemirrorField ItemContentRichEditor">
    <div
        v-if="!diffRows"
        class="p-2"
    >
        {{ $t("computing") }}
    </div>

    <div
        v-else
        class="flex flex-col RichTextStyling p-1"
    >
        <div
            v-for="diffRow in diffRows"
            class="ItemContentDiff__panels"
            :key="diffRow.id"
        >
            <div
                class="ItemContentDiff__panel w-1/2 p-1"
                :class="{
                    'bg-gray-300': !diffRow.leftEditor,
                    'bg-red-100': diffRow.leftEditor && diffRow.hasRemovedContent,
                    'text-gray-500': !diffRow.changes.length,
                }"
            >
                <p
                    v-if="!diffRow.leftEditor"
                    class="text-center"
                >
                    ∅
                </p>
                <EditorContent
                    v-else
                    :editor="diffRow.leftEditor"
                />
            </div>

            <div
                class="ItemContentDiff__panel w-1/2 p-1"
                :class="{
                    'bg-gray-300': !diffRow.rightEditor,
                    'bg-green-100': diffRow.rightEditor && diffRow.hasAddedContent,
                    'text-gray-500': !diffRow.changes.length,
                }"
            >
                <p
                    v-if="!diffRow.rightEditor"
                    class="text-center"
                >
                    ∅
                </p>
                <EditorContent
                    v-else
                    :editor="diffRow.rightEditor"
                />
            </div>
        </div>
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import { EditorContent } from "tiptap"
import { EMPTY_PROSEMIRROR_DOC, itemContentSchema } from "@richText/schema"
import { DocDiff } from "@js/diff/docDiff"
import { DiffRowsComputer } from "@js/diff/diffRows"

export default {
    name: "ItemContentDiffProsemirrorField",
    mixins: [PilotMixin],
    components: {
        EditorContent,
    },
    props: {
        fieldSchema: Object,
        itemReadOnly: Object,
    },
    data: () => ({
        // A prosemirror Node object that represent the old document
        oldDoc: null,
        // A prosemirror Node object that represent the new document
        newDoc: null,

        // A DocDiff instance, oldDoc -> newDoc
        diffOldToNew: null,
        // A DocDiff instance, newDoc  -> oldDoc
        // !! WARNING : this diff is inverted !!
        diffNewToOld: null,

        // A list of DiffRow object containing the data for one paragraph.
        diffRows: null,
        // For big documents, we display a feedback to the user
        computing: false,
    }),
    computed: {
        fieldName() {
            return this.fieldSchema.name
        },
        fieldDiff() {
            return this.itemReadOnly.fieldDiffs[this.fieldName]
        },
        oldDocJSON() {
            // May be undefined because of elastic fields
            return this.fieldDiff.old_value || EMPTY_PROSEMIRROR_DOC
        },
        newDocJSON() {
            // May be undefined because of elastic fields
            return this.fieldDiff.new_value || EMPTY_PROSEMIRROR_DOC
        },
    },
    methods: {
        /**
         * Recompute all the data needed to display the merge diff for this field.
         * Should be called at init, or when the content of one side of the diff has changed.
         */
        updateDiff() {
            // Get a prosemirror Node from the JSON, for the old and new documents
            this.oldDoc = itemContentSchema.nodeFromJSON(this.oldDocJSON)
            this.newDoc = itemContentSchema.nodeFromJSON(this.newDocJSON)

            // Compute the diff from old to new
            this.diffOldToNew = new DocDiff(this.oldDoc, this.newDoc, { isInverted: false })

            // Note that this diff is inverted
            this.diffNewToOld = new DocDiff(this.newDoc, this.oldDoc, { isInverted: true })

            this.updateDiffRows()
        },

        updateDiffRows() {
            this.computing = true

            new DiffRowsComputer(
                this.oldDoc,
                this.newDoc,
                this.diffOldToNew.changes,
                this.diffNewToOld.changes,
            )
                .computeDiffRows()
                .then((diffRows) => {
                    this.diffRows = diffRows
                })

            this.computing = false
        },
    },
    watch: {
        "itemReadOnly.fieldDiffs": {
            deep: true,
            handler() {
                this.updateDiff()
            },
        },
        editSessionForMergeTool() {
            this.updateDiff()
        },
    },
    mounted() {
        this.updateDiff()
    },
    i18n: {
        messages: {
            fr: {
                computing: "Calcul en cours...",
            },
            en: {
                computing: "Computing...",
            },
        },
    },
}
</script>
