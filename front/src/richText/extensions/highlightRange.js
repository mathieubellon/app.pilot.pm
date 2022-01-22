import $ from "jquery"
import { Extension, Plugin, PluginKey } from "tiptap"
import { Decoration, DecorationSet } from "prosemirror-view"

const highlightRangeKey = new PluginKey("highlightRange")

/**
 * One range of the document to highlight.
 *
 * If the text is not present in the document, set deleted=true
 * to display a void mark (∅) at the deleted position.
 */
class HighlightedRange {
    constructor(from, to, deleted) {
        this.from = from
        this.to = to
        this.deleted = deleted
    }
}

/**
 * Prosemirror plugin that manage the display of Change objects in the document
 * so the user can visualize them.
 *
 * Use prosemirror Decorations to modify the document structure.
 */
const highlightRangePlugin = new Plugin({
    state: {
        init: () => ({
            highlightRangeDecorations: DecorationSet.empty,
        }),
        apply: (transaction, prev, state) => {
            let action = transaction.getMeta(highlightRangeKey) || {}

            switch (action.type) {
                case "emptyHighlightedRanges":
                    return {
                        highlightRangeDecorations: DecorationSet.empty,
                    }
                case "setHighlightedRanges":
                    let decorations = [],
                        decoration
                    for (let highlightedRange of action.highlightedRanges) {
                        if (highlightedRange.deleted) {
                            let deletionWidget = $(
                                '<span class="highlight-range-style">∅</span>',
                            ).get(0)
                            let pos = Math.min(highlightedRange.from, state.doc.content.size)
                            decoration = Decoration.widget(pos, deletionWidget)
                        } else {
                            decoration = Decoration.inline(
                                highlightedRange.from,
                                highlightedRange.to,
                                {
                                    class: "highlight-range-style",
                                },
                            )
                        }
                        decorations.push(decoration)
                    }

                    return {
                        highlightRangeDecorations: DecorationSet.create(state.doc, decorations),
                    }
                default:
                    return prev
            }
        },
    },

    props: {
        decorations(state) {
            return this.getState(state).highlightRangeDecorations
        },
    },

    key: highlightRangeKey,
})

class HighlightRange extends Extension {
    get name() {
        return "HighlightRange"
    }

    get defaultOptions() {
        return {
            publishHighlightRange: (highlightedRanges) => {
                const { state, view } = this.editor

                if (!highlightedRanges) {
                    view.dispatch(
                        state.tr.setMeta(highlightRangeKey, {
                            type: "emptyHighlightedRanges",
                        }),
                    )
                } else {
                    view.dispatch(
                        state.tr.setMeta(highlightRangeKey, {
                            type: "setHighlightedRanges",
                            highlightedRanges,
                        }),
                    )
                }
            },
        }
    }

    get plugins() {
        return [highlightRangePlugin]
    }
}

export { HighlightRange, HighlightedRange }
