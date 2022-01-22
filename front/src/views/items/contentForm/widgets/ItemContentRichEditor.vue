<template>
<div class="ItemContentRichEditor">
    <RichTextEditor
        :annotationManager="annotationManager"
        :editor="editor"
        :menuBarCanFade="true"
        :readOnly="readOnly"
    />
</div>
</template>

<script>
/**
 *  WARNING : This component may be used inside the Item Detail view,
 *  but also inside other components (like ItemAddForm),
 *  which doesnt not have access to the detail store data.
 *  Store access should be carefully checked.
 */

import _ from "lodash"
import $ from "jquery"

import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { Editor, EditorContent, EditorMenuBubble } from "tiptap"
import { Slice, Fragment } from "prosemirror-model"
import { sendableSteps } from "prosemirror-collab"
import { insertPoint } from "prosemirror-transform"
import PilotMixin from "@components/PilotMixin"
import { getRandomId } from "@js/utils"

import $monitoring from "@js/monitoring"
import { annotationPlugin } from "@richText/extensions/annotations"
import { itemContentSchema } from "@richText/schema"
import { Collab } from "@richText/extensions/collab"
import { removeEmptyParagraphsFromSlice } from "@richText/cleaning"
import { isImageSelected } from "@richText/utils"
import { getCurrentItemScroll, scrollItemTo } from "@js/items/itemsUtils"

import TextAnnotationsManager from "../annotations/text/TextAnnotationsManager"
import RichTextEditor from "@richText/RichTextEditor"

const HUGE_DOCUMENT_LIMIT = 30000
const BIG_DOCUMENT_LIMIT = 15000
const BIG_DOCUMENT_DEBOUNCE_TIME = 1000 // In milliseconds
const SELECTION_UPDATE_THROTTLE_TIME = 2000 // In milliseconds

let hugeDocumentAlertDone = false

export default {
    name: "ItemContentRichEditor",
    mixins: [PilotMixin],
    components: {
        EditorContent,
        EditorMenuBubble,
        RichTextEditor,
    },
    props: {
        schema: Object,
        value: Object,
        readOnly: {
            type: Boolean,
            default: false,
        },
        annotations: {},
    },
    data: () => ({
        editor: null,
        annotationManager: null,
        // A flag to prevent emitting back when we're rendering the value prop
        isRenderingValue: false,
    }),
    computed: {
        ...mapState("itemDetail", ["editable"]),
        ...mapGetters("itemDetail", ["isDiffModeActive"]),
        ...mapState("itemContentForm", [
            "itemId",
            "myRealtimeClientId",
            "myRealtimeUser",
            "realtimeUsers",
        ]),
    },
    methods: {
        ...mapMutations("itemContentForm", ["registerTiptapEditor", "registerAnnotationManager"]),
        ...mapActions("itemContentForm", ["deselectAllAnnotations", "alertBase64Image"]),
        exposePmApi() {
            if (this.registerTiptapEditor) {
                this.registerTiptapEditor({
                    fieldName: this.schema.name,
                    editor: this.editor,
                    readOnly: this.readOnly,
                })
            }

            if (this.annotationManager) {
                this.registerAnnotationManager({
                    key: this.schema.name,
                    annotationManager: this.annotationManager,
                    readOnly: this.readOnly,
                })
            }
        },
        emitValueChange() {
            let { from, to } = this.editor.state.selection
            let inputData = {
                value: this.editor.getJSON(),
                selection: { from, to },
            }

            if (this.myRealtimeClientId) {
                // sendable steps corresponds to the changes we made in our local editor.
                // They may be rebased on remote steps received from the realtime server.
                const sendable = sendableSteps(this.editor.state)
                // When we integrate steps from remote users,
                // and if we did not made changes in our local editor,
                // then the sendable steps will be empty.
                // That means the user did not actually made an input,
                // we must not emit an event
                if (!sendable) {
                    return
                }
                inputData.steps = sendable.steps.map((step) => step.toJSON())
            }
            if (this.annotationManager) {
                inputData.annotations = this.annotationManager.annotations
            }
            this.$emit("input", inputData)
        },
        debouncedEmitValueChange: _.debounce(function () {
            this.emitValueChange()
        }, BIG_DOCUMENT_DEBOUNCE_TIME),
        onValueChange() {
            let isBigDocument = this.editor.state.doc.content.size > BIG_DOCUMENT_LIMIT
            let isHugeDocument = this.editor.state.doc.content.size > HUGE_DOCUMENT_LIMIT

            if (isHugeDocument && !hugeDocumentAlertDone) {
                $monitoring.captureMessage(`Item ${this.itemId} has reached a huge size`)
                hugeDocumentAlertDone = true
            }

            if (isBigDocument) {
                this.debouncedEmitValueChange()
            } else {
                this.emitValueChange()
            }
        },

        throttledSelectionUpdate: _.throttle(function (selection) {
            this.$emit("selection", selection)
        }, SELECTION_UPDATE_THROTTLE_TIME),

        /**
         * When there's a transaction to dispatch, we do the following :
         *  - If the document has changed, emit a doc changed event
         *  - If the selection has changed, display the associated annotations
         */
        onTransaction({ transaction }) {
            // Don't emit anything when we're rendering the value prop
            if (this.isRenderingValue) {
                return
            }

            // Update the binded model whith the new state
            // When Prosemirror update content we need to tell Vue about current document
            if (transaction.docChanged) {
                this.onValueChange()
            }

            // If the selection has changed...
            if (transaction.selectionSet) {
                // ...select annotations on the cursor
                let selection = transaction.selection

                if (this.annotationManager && (selection.empty || isImageSelected(selection))) {
                    this.annotationManager.selectAnnotationsAtPosition(selection.from)
                }

                let { from, to } = selection
                this.throttledSelectionUpdate({ from, to })
            }
        },

        /**
         *  Render the value prop into the prosemirror editor
         *
         * This will :
         *  - Updating the prosemirror document  (from the model json)
         *  - Updating the annotations
         *  - Publish the decorations for the diff
         */
        renderValue() {
            if (!this.value) {
                return
            }

            let oldDocJSON = this.editor.getJSON(),
                newDocJSON = this.value

            /**
             * The binded value can be updated either by :
             * 1/ A user input on the prosemirror widget, which is emitted and propagated back on the value prop
             * 2/ An external change, for example a restoreEditSession
             *
             * Update the document state only when the document did actually change, in the case 2
             */
            if (!_.isEqual(oldDocJSON, newDocJSON)) {
                // Remember the scroll position, to keep the user into his current context
                let oldScrollTop = getCurrentItemScroll()

                // Apply the new state to the editor view
                this.isRenderingValue = true
                this.editor.setContent(newDocJSON)
                this.isRenderingValue = false

                // Restore the scroll position
                scrollItemTo({ topCoord: oldScrollTop })

                // We need to redraw the annotation after the content changed
                this.renderAnnotations()
            }

            // We need to show a visual indication of the carriage return to the user
            // when we are in diff mode, otherwise the diff is cryptic when hard breaks are moved around.
            // No luck with the ::before css pseudo-selector, because they are not applied to br element...
            // The NodeView way is not great either, because they aren't applied to the Decoration.widget we use
            // for the inserted content.
            // Instead, we brute force the display here by replacing the <br /> with some enhanced markup.
            if (this.isDiffModeActive && !this.editable) {
                this.$nextTick(() => {
                    $(this.$el)
                        .find(
                            ".diff-inserted br, .diff-deleted br, br.diff-inserted, br.diff-deleted",
                        )
                        .not(".hardbreak-marker")
                        .each((index, elem) => {
                            $(elem).replaceWith(
                                $("<span></span>")
                                    .attr("class", $(elem).attr("class"))
                                    .append("⏎")
                                    .append($('<br class="hardbreak-marker" />')),
                            )
                        })
                })
            }
        },

        renderAnnotations() {
            if (!this.annotationManager) {
                return
            }
            // This will redraw the annotations
            this.annotationManager.setAnnotations(
                this.annotations ? this.annotations[this.schema.name] : {},
            )
        },

        renderCursorDecorations() {
            if (!this.editor.extensions.options.Collab || this.readOnly) {
                return
            }

            this.editor.extensions.options.Collab.updateCursors(
                // Render only the cursor of users focused on this field
                this.realtimeUsers.filter((user) => user.field_focus == this.schema.name),
            )
        },

        transformPasted(slice) {
            slice = removeEmptyParagraphsFromSlice(slice)

            /**
             * As per prosemirror doc, nodes are supposed to be immutable,
             * and we shouldn't modify them directly. BUT :
             * 1/ Here the slice has been created from scratch with the pasted content,
             *    and is not part of a document
             * 2/ It's much much more complicated to create a new slice with copies of the image nodes.
             * */
            slice.content.descendants((node, pos, parent) => {
                let nodeAttrs = node.attrs
                if (
                    node.type.name == "image" &&
                    nodeAttrs.src.includes("data:image") &&
                    nodeAttrs.src.includes("base64,")
                ) {
                    // Base64 conversion taken from https://stackoverflow.com/a/38935990
                    let array = nodeAttrs.src.split(","),
                        mime = array[0].match(/:(.*?);/)[1],
                        bstr = atob(array[1]),
                        n = bstr.length,
                        u8arr = new Uint8Array(n),
                        filename = nodeAttrs.title || nodeAttrs.alt || nodeAttrs.caption || "image"

                    while (n--) {
                        u8arr[n] = bstr.charCodeAt(n)
                    }
                    let file = new File([u8arr], filename, { type: mime })

                    let uploadId = getRandomId()
                    this.editor.uploadedFiles[uploadId] = file
                    node.type = this.editor.schema.nodes.imageUpload
                    node.attrs = { uploadId }
                }
            })

            return slice
        },

        handleDOMPasteOrDrop(pmView, event) {
            let clipboardFiles = _.get(event, "clipboardData.files") || []
            let dataTransferFiles = _.get(event, "dataTransfer.files") || []

            if (clipboardFiles.length > 0 || dataTransferFiles.length > 0) {
                event.preventDefault()
                event.stopImmediatePropagation()
                let schema = this.editor.schema

                if (dataTransferFiles.length > 0) {
                    let pos = pmView.posAtCoords({ left: event.clientX, top: event.clientY })
                    if (!pos) {
                        return
                    }

                    let insertionPosition = insertPoint(
                        this.editor.state.doc,
                        pos.pos,
                        schema.nodes.imageUpload,
                    )
                    if (!insertionPosition) {
                        return
                    }

                    for (let file of dataTransferFiles) {
                        let uploadId = getRandomId()
                        this.editor.uploadedFiles[uploadId] = file
                        this.editor.dispatchTransaction(
                            this.editor.state.tr.insert(
                                insertionPosition,
                                schema.nodes.imageUpload.create({ uploadId }),
                            ),
                        )
                    }
                }

                if (clipboardFiles.length > 0) {
                    for (let file of clipboardFiles) {
                        let uploadId = getRandomId()
                        this.editor.uploadedFiles[uploadId] = file
                        this.editor.dispatchTransaction(
                            this.editor.state.tr.replaceSelectionWith(
                                schema.nodes.imageUpload.create({ uploadId }),
                            ),
                        )
                    }
                }

                // Return true to prevent default prosemirror handling
                return true
            }
        },

        handlePasteOrDrop(pmView, event, slice) {
            if (slice == null) {
                return false
            }

            // base64 encoded image should never reach this hook,
            // because they are handled in transformPasted.
            // But we never know, better be safe than sorry.
            let sliceString = JSON.stringify(slice.toJSON())
            let hasImage = sliceString.includes("data:image") && sliceString.includes("base64,")
            if (hasImage) {
                this.alertBase64Image()
                // Return true to prevent default prosemirror handling
                return true
            }
        },
    },
    watch: {
        /**
         * When the value prop change, re-render the prosemirror editor.
         */
        value() {
            this.renderValue()
        },

        /**
         * When the annotation change, make a restoration on the annotationManager
         */
        annotations: {
            handler() {
                this.renderAnnotations()
            },
            deep: true,
        },

        realtimeUsers() {
            this.renderCursorDecorations()
        },
    },
    created() {
        let extensions = itemContentSchema.getExtensions()

        if (this.myRealtimeClientId) {
            extensions = [
                ...extensions,
                // Add the collab module
                new Collab({
                    userId: this.myRealtimeUser.id,
                    clientId: this.myRealtimeClientId,
                }),
            ]
        }

        this.editor = new Editor({
            content: this.value,
            editable: !this.readOnly,
            extensions: extensions,
            onTransaction: this.onTransaction,
            serializer: itemContentSchema.DOMSerializer,
            injectCSS: false,
        })
        this.editor.itemId = this.itemId
        this.editor.uploadedFiles = {}
        this.editor.$store = this.$store

        // Override tiptap default props
        this.editor.view.setProps({
            handlePaste: this.handlePasteOrDrop,
            handleDrop: this.handlePasteOrDrop,
            handleDOMEvents: {
                drop: this.handleDOMPasteOrDrop,
                paste: this.handleDOMPasteOrDrop,
            },
            transformPasted: this.transformPasted,
        })

        // Setup the annotation manager
        if (this.myRealtimeClientId) {
            this.annotationManager = new TextAnnotationsManager(
                this.myRealtimeUser,
                this.editor.view,
            )
            this.annotationManager.on("update", (annotations) => {
                this.$emit("annotations", { annotations })
            })
            this.annotationManager.on("select", ({ deselectOther }) => {
                if (deselectOther) {
                    this.deselectAllAnnotations({ exclude: this.annotationManager })
                }
            })
            this.editor.registerPlugin(annotationPlugin(this.annotationManager))
        }

        // Prosemirror is set up, expose the external API
        this.exposePmApi()
    },
    mounted() {
        // Render the initial annotations once the editor is mounted
        this.renderAnnotations()
    },
    beforeDestroy() {
        this.editor.destroy()
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";
@import "~@sass/mixins.scss";

/* ==========================================================================
   Prosemirror Content
   ========================================================================== */

$annotation-yellow: #ffff00;

.ItemContentRichEditor {
    .ProseMirror {
        // Highlight a range
        .highlight-range-style {
            background: $orangedeep200;
        }

        // The more annotations there is on a chunk of text,
        // the more dark get the background
        .annotationStyle-4 {
            background: darken($annotation-yellow, 30%);
        }

        .annotationStyle-3 {
            background: darken($annotation-yellow, 20%);
        }

        .annotationStyle-2 {
            background: darken($annotation-yellow, 10%);
        }

        .annotationStyle-1 {
            background: $annotation-yellow;
        }

        // Other user's cursors
        .cursor {
            position: absolute; // Remove the widget from the flow
            height: 1.3em;
            width: 2px;
            transform: translate(-1px, 3px);
        }

        // Annotated img get an overlay above them
        .img-annotation-overlay {
            position: absolute;
            display: inline-block;
            opacity: 0.4;
        }
    }
}

/* ==========================================================================
   Small Desktop
   ========================================================================== */
// De-centering commented for now
/*
@media only screen and (max-width: $breakpointLargeDesktop) {
  .ItemDetailBody__editorContainerPanel{
    margin-left:0;

    .ItemDetailTextAnnotations,{
      @include itemDecorationBoxesWidth($widthDecorationBoxReduced);
    }
  }
}
*/
/* ==========================================================================
   Tablet
   ========================================================================== */

/*
@media only screen and (max-width: 639px) {
    .ItemDetailTextAnnotations{
        padding: 0 15px;

        .AnnotationElement {
            margin-top: 30px;
        }
    }
}

@media only screen and (min-width: $breakpointMobile + 1) and (max-width: 639px) {
    .ItemDetailTextAnnotations{
        width: auto;
        left: $widthNav !important; // Surcharge js
    }
}
*/

/* ==========================================================================
   Mobile
   ========================================================================== */

/*
@media only screen and (max-width: $breakpointMobile) {
    .ItemContentRichEditor .ProseMirror {
        padding: 10px;
    }

    .ItemDetailTextAnnotations{
        left: 0 !important; // Surcharge js
    }
}
*/
</style>
