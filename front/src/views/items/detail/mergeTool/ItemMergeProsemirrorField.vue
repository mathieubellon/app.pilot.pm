<template>
<div class="ItemMergeProsemirrorField ItemContentRichEditor">
    <div
        v-if="mergeError"
        class="alert-panel is-red"
    >
        {{ $t("mergeError") }}
    </div>

    <div
        v-else-if="!diffRows"
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
            class="ItemContentMergeTool__panels"
            :key="diffRow.id"
        >
            <div
                class="ItemContentMergeTool__panel w-2/5 p-1"
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
                class="ItemContentMergeTool__panel w-2/5 p-1"
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

            <div class="ItemContentMergeTool__panel w-1/5">
                <div
                    v-for="(change, changeIndex) in diffRow.changes"
                    class="border p-2 bg-white"
                    :class="{ 'mt-1': changeIndex > 0 }"
                    :key="change.id"
                >
                    <div
                        v-if="!change.isBLock"
                        class="mb-1"
                    >
                        <del
                            v-if="change.getRemovedHtmlString()"
                            v-html="change.getRemovedHtmlString()"
                        />
                        <template
                            v-if="change.getRemovedHtmlString() && change.getAddedHtmlString()"
                        >
                            -->
                        </template>
                        <ins
                            v-if="change.getAddedHtmlString()"
                            v-html="change.getAddedHtmlString()"
                        />
                    </div>

                    <button
                        v-if="change.accepted"
                        class="button is-indigo"
                        @click="toggleChange(change)"
                    >
                        {{ $t("rejectChange") }}
                    </button>
                    <button
                        v-else
                        class="button is-teal"
                        @click="toggleChange(change)"
                    >
                        {{ $t("acceptChange") }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import $monitoring from "@js/monitoring"
import PilotMixin from "@components/PilotMixin"

import { Editor, EditorContent } from "tiptap"
import { Step, Mapping } from "prosemirror-transform"
import { EMPTY_PROSEMIRROR_DOC, itemContentSchema } from "@richText/schema"
import { DocDiff } from "@js/diff/docDiff"
import { DiffRowsComputer } from "@js/diff/diffRows"

/**
 * There's 3 documents managed here :
 *  - The old document, which correspond to an old version of the item. Displayed on the left side.
 *  - The current document, which correspond to actual state of the item.
 *  - The merged document, which is the result of merging the old into the new, taking into account the rejected changes.
 *
 *  The old document is displayed on the left, the merged document is displayed on the right.
 *
 *  To align the two sides of the diff, we split the documents in top-level Nodes.
 *  We store those paragraphs in a list of "diffRow".
 *  Each diffRow contains one or two editors ( left and/or right ), and each editors may contains one or more Nodes,
 *  depending on the Nodes which have been added, removed, or edited inline.
 *  It also contains the changes needed to go from one editor to the other.
 */
export default {
    name: "ItemMergeProsemirrorField",
    mixins: [PilotMixin],
    components: {
        EditorContent,
    },
    props: {
        fieldSchema: Object,
    },
    data: () => ({
        // A prosemirror Node object that represent the current document
        oldDoc: null,
        // A prosemirror Node object that represent the merged document
        mergedDoc: null,

        // A DocDiff instance, oldDoc -> currentDoc
        diffOldToCurrent: null,
        // A DocDiff instance, mergedDoc  -> oldDoc
        // !! WARNING : this diff is inverted !!
        diffMergedToOld: null,

        // A list of DiffRow object containing the data for one paragraph.
        diffRows: null,
        // For big documents, we display a feedback to the user
        computing: false,

        // A flag if we could not apply the changes to generate the mergedDoc
        mergeError: false,
    }),
    computed: {
        ...mapState("itemDetail", ["editSessionForMergeTool", "item"]),
        ...mapState("itemContentForm", ["itemEditable"]),
        fieldName() {
            return this.fieldSchema.name
        },
        oldDocJSON() {
            // May be undefined because of elastic fields
            return this.editSessionForMergeTool.content[this.fieldName] || EMPTY_PROSEMIRROR_DOC
        },
        currentDocJSON() {
            // May be undefined because of elastic fields
            return this.itemEditable.content[this.fieldName] || EMPTY_PROSEMIRROR_DOC
        },
    },
    methods: {
        /**
         * Recompute all the data needed to display the merge diff for this field.
         * Should be called at init, or when the content of one side of the diff has changed.
         */
        updateDiff() {
            // Get a prosemirror Node from the JSON, for the old and current documents
            this.oldDoc = itemContentSchema.nodeFromJSON(this.oldDocJSON)
            let currentDoc = itemContentSchema.nodeFromJSON(this.currentDocJSON)

            // Compute the diff from old to current
            this.diffOldToCurrent = new DocDiff(this.oldDoc, currentDoc, { isInverted: false })

            this.updateMergedDoc()
        },

        /**
         * Recompute the results of the merge, taking into account the accepted/rejected changes.
         * Should be called at init, or when one of the change has been accepted/rejected.
         */
        updateMergedDoc() {
            this.mergeError = false

            let editor = new Editor({
                extensions: itemContentSchema.getExtensions(),
                content: this.oldDocJSON,
                injectCSS: false,
            })

            let mapping = new Mapping()
            let initialState = editor.state
            let transaction = initialState.tr
            let mergedStep = null,
                previousStep = null,
                currentStep

            let applyStep = (step) => {
                let stepResult = transaction.maybeStep(step)
                if (stepResult.failed) {
                    $monitoring.captureMessage("Item merge error : " + stepResult.failed, {
                        itemId: this.item.id,
                        version: this.editSessionForMergeTool.version,
                        step: step.toJSON(),
                    })
                    this.mergeError = true
                }
            }

            for (let change of this.diffOldToCurrent.changes) {
                if (!change.accepted) {
                    continue
                }

                let stepJson = change.step.toJSON()
                let step = Step.fromJSON(editor.schema, stepJson)

                // Re-map the step with the previous position modifications
                currentStep = step.map(mapping)

                // Update the global mapping with the new positions from the current step
                mapping.appendMap(currentStep.getMap())

                if (!mergedStep) {
                    // The first step of the merge
                    mergedStep = currentStep
                } else {
                    previousStep = mergedStep
                    // Will return the merged step if successful, or null if it fails
                    mergedStep = previousStep.merge(currentStep)
                    // The merge failed, apply the previous merged steps.
                    if (!mergedStep) {
                        applyStep(previousStep)
                        // Start a new merge round
                        mergedStep = currentStep
                    }
                }

                if (this.mergeError) {
                    mergedStep = null
                    break
                }
            }

            // Apply the last step (or steps if there's multiple steps merged together)
            if (mergedStep) {
                applyStep(mergedStep)
            }

            if (this.mergeError) {
                return
            }

            let mergedState = initialState.apply(transaction)
            this.mergedDoc = mergedState.doc

            // Note that this diff is inverted
            this.diffMergedToOld = new DocDiff(this.mergedDoc, this.oldDoc, { isInverted: true })

            this.updateDiffRows()

            this.emitChange()
        },

        /**
         *  Recompute all diffRows, when the merged doc has changed.
         */
        updateDiffRows() {
            this.computing = true

            new DiffRowsComputer(
                this.oldDoc,
                this.mergedDoc,
                this.diffOldToCurrent.changes,
                this.diffMergedToOld.changes,
            )
                .computeDiffRows()
                .then((diffRows) => {
                    this.diffRows = diffRows
                })

            this.computing = false
        },

        /**
         * Notify the parent component, when the merged doc has changed.
         */
        emitChange() {
            let mergedJSON = this.mergedDoc.toJSON()

            let docDiff = new DocDiff(
                itemContentSchema.nodeFromJSON(this.currentDocJSON),
                itemContentSchema.nodeFromJSON(mergedJSON),
            )
            this.$emit("mergeChange", {
                fieldName: this.fieldName,
                value: mergedJSON,
                steps: docDiff.changes.map((change) => change.step.toJSON()),
            })
        },

        /**
         * Accept/reject one change. Will update the merged doc.
         */
        toggleChange(change) {
            if (!change) {
                return
            }
            // The accepted property is reactive, it will be updated in the template.
            change.accepted = !change.accepted
            // When a change is toggled, the merged document must be updated, and the diffRows
            this.updateMergedDoc()
        },
    },
    /**
     * Recompute the whole diff when the content change, and at init.
     */
    watch: {
        "itemEditable.content": {
            deep: true,
            handler() {
                this.updateDiff()
            },
        },
        editSessionForMergeTool() {
            this.updateDiff()
        },
    },
    created() {
        this.updateDiff()
    },
    i18n: {
        messages: {
            fr: {
                acceptChange: "Conserver cette modification",
                computing: "Calcul en cours...",
                mergeError: "Erreur de fusion",
                rejectChange: "Rejeter cette modification",
            },
            en: {
                acceptChange: "Accept this change",
                computing: "Computing...",
                mergeError: "Merge error",
                rejectChange: "Reject this change",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.ItemMergeProsemirrorField__change {
    border: solid 1px $gray;
    margin-bottom: 0.5em;
    padding: 0.5em;
}
</style>
