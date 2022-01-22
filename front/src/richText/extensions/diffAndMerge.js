import $ from "jquery"
import { Extension, Plugin, PluginKey } from "tiptap"
import { Decoration, DecorationSet } from "prosemirror-view"

const diffAndMergeKey = new PluginKey("diffAndMerge")

/***********************
 * Decorating Prosemirror with doc changes
 ************************/

/**
 * Create the prosemirror Decoration object(s) necessary to indicate to the user
 * the text modified by a Change object on the original document.
 *
 * The created decorations will be pushed into the decorations array passed as first parameter
 */
function addDecorationForChange(
    decorations,
    change,
    { isInverted, showInsertions, showDeletions },
) {
    let step = change.step

    if (!step) {
        return null
    }

    let inlineFragment = change.getRemovedDOMFragment(),
        widgetFragment = change.getAddedDOMFragment(),
        widgetIsBlock = change.addedBlockLength,
        showInline,
        showWidget
    let inlineClass, widgetClass, widgetPos, widgetWrapper
    if (isInverted) {
        // When inverted, the "removed" fragment correspond to the inserted content, and is inline
        // The "added" fragment correspond to the deleted content, and is widget
        inlineClass = "diff-inserted"
        widgetClass = "diff-deleted"
        widgetPos = step.from // Display the deleted content *before* the inserted content
        widgetWrapper = "del"
        showInline = showInsertions
        showWidget = showDeletions
    } else {
        // When not-inverted, the "removed" fragment correspond to the deleted content, and is inline
        // and the "added" fragment correspond to the inserted content, and is widget
        inlineClass = "diff-deleted"
        widgetClass = "diff-inserted"
        widgetPos = step.to // Display the inserted content *after* the deleted content
        widgetWrapper = "ins"
        showInline = showDeletions
        showWidget = showInsertions
    }

    // Inline content
    if (inlineFragment && step.from != step.to && showInline) {
        let attrs = {
            class: inlineClass,
        }

        let inlineContent = inlineFragment.firstChild

        // For inserted empty paragraph, use a node decoration so it can be displayed correctly
        if (inlineContent.nodeName.toLowerCase() == "p" && inlineContent.innerHTML == "") {
            decorations.push(Decoration.node(step.from, step.to, attrs))
        } else {
            decorations.push(Decoration.inline(step.from, step.to, attrs))
        }
    }

    // Widget content
    if (widgetFragment && showWidget) {
        function addWidget(widgetContent) {
            widgetContent.setAttribute("class", widgetClass)
            decorations.push(Decoration.widget(widgetPos, widgetContent))
        }

        let widgetContent
        if (widgetIsBlock) {
            for (let widgetContent of widgetFragment.children) {
                // Add a <br /> to empty paragraph so they can appear into the prosemirror editor.
                if (widgetContent.nodeName.toLowerCase() == "p" && widgetContent.innerHTML == "") {
                    widgetContent.appendChild($('<br class="hardbreak-marker" />')[0])
                }
                addWidget(widgetContent)
            }
        } else {
            widgetContent = document.createElement(widgetWrapper)
            widgetContent.appendChild(widgetFragment)
            addWidget(widgetContent)
        }
    }
}

/**
 * Prosemirror plugin that manage the display of Change objects in the document
 * so the user can visualize them.
 *
 * Use prosemirror Decorations to modify the document structure.
 */
let diffAndMergePlugin = new Plugin({
    key: diffAndMergeKey,

    state: {
        init: (config) => ({
            changeDecorations: DecorationSet.empty,
        }),
        apply: function (transaction, prev, state) {
            let action = transaction.getMeta(diffAndMergeKey) || {}

            if (action.type != "docDiff") {
                return prev
            }

            let decorations = []
            for (let change of action.changes || []) {
                addDecorationForChange(decorations, change, action)
            }

            return {
                changeDecorations: DecorationSet.create(state.doc, decorations),
            }
        },
    },

    props: {
        decorations(state) {
            return this.getState(state).changeDecorations
        },
    },
})

class DiffAndMerge extends Extension {
    get name() {
        return "DiffAndMerge"
    }

    get defaultOptions() {
        return {
            /**
             * Decorate a list of Changes into a prosemirror editor
             */
            publishChanges: (
                changes,
                { isInverted = false, showInsertions = true, showDeletions = true } = {},
            ) => {
                const { state, view } = this.editor

                view.dispatch(
                    state.tr.setMeta(diffAndMergeKey, {
                        type: "docDiff",
                        changes,
                        isInverted,
                        showInsertions,
                        showDeletions,
                    }),
                )
            },
        }
    }

    get plugins() {
        return [diffAndMergePlugin]
    }
}

export { DiffAndMerge, diffAndMergePlugin }
