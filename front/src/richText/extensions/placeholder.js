import { Extension, Plugin, PluginKey } from "tiptap"
import { Decoration, DecorationSet } from "prosemirror-view"

const placeholderKey = new PluginKey("placeholder")

// We can't use '@js/i18n' here because that's incompatible with
// a usage inside node.js which is done by serializePmDoc.js
let defaultPlaceholder = {
    fr: "Saisissez votre texte ici",
    en: "Type your text here",
}

/**
 * Compute the DecorationSet to represent the placeholder.
 * An empty document will display an "Please Enter text" placeholder.
 * A non-empty doc will display markers at the position of empty paragraphs.
 *
 * @param doc prosemirror Document
 * @returns The DecorationSet for the placeholder
 */
const placeholderPlugin = new Plugin({
    key: placeholderKey,

    state: {
        // The last plugin is created by Tiptap to hold any extra editorProps we pass to him during creation.
        // Retreive the placeholder from there
        init: (config) => ({
            placeholder: config.plugins[config.plugins.length - 1].props.placeholder,
        }),
        apply: (transaction, prev) => prev,
    },

    props: {
        decorations(state) {
            const editablePlugin = state.plugins.find((plugin) =>
                plugin.key.startsWith("editable$"),
            )
            // Show placeholder only when the editor is in editable mode
            if (!editablePlugin.props.editable()) {
                return DecorationSet.empty
            }

            let pluginState = this.getState(state),
                doc = state.doc

            // An empty doc has a size of 4 : "open doc" "open paragraph" "close paragraph" "close doc"
            if (doc.nodeSize == 4) {
                let placeholder = pluginState ? pluginState.placeholder : null
                if (!placeholder) {
                    placeholder = defaultPlaceholder[window.pilot.currentLocale]
                }

                let placeholderNode = Decoration.node(0, 2, {
                    class: "empty-paragraph",
                    "data-empty-text": placeholder,
                })
                return DecorationSet.create(doc, [placeholderNode])
            }

            // Non-empty doc : look for empty paragraph
            let decorations = []
            let pos = 0
            for (let i = 0; i < doc.content.content.length; i++) {
                const node = doc.content.content[i]
                if (node.type.name === "paragraph" && node.textContent === "") {
                    decorations.push(
                        Decoration.node(pos, pos + 2, {
                            class: "empty-paragraph",
                            "data-empty-text": "¶",
                        }),
                    )
                }
                pos += node.nodeSize
            }
            return DecorationSet.create(doc, decorations)
        },
    },
})

export class Placeholder extends Extension {
    get name() {
        return "Placeholder"
    }

    get plugins() {
        return [placeholderPlugin]
    }
}
