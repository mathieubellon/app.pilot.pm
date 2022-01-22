import { Extension, Plugin, PluginKey } from "tiptap"
import { DecorationSet, Decoration } from "prosemirror-view"

export class Selection extends Extension {
    get name() {
        return "Selection"
    }

    get defaultOptions() {
        return {
            className: "selected-node",
        }
    }

    get plugins() {
        return [
            new Plugin({
                props: {
                    decorations: ({ doc, plugins, selection }) => {
                        const editablePlugin = plugins.find((plugin) =>
                            plugin.key.startsWith("editable$"),
                        )
                        const editable = editablePlugin.props.editable()
                        const active = editable && this.options.className
                        const { focused } = this.editor
                        const { from, to } = selection
                        const decorations = []

                        if (!active || !focused || from == to) {
                            return false
                        }

                        doc.descendants((node, pos) => {
                            const isSelected = from <= pos + node.nodeSize && to > pos

                            if (isSelected && !node.isText) {
                                const decoration = Decoration.node(pos, pos + node.nodeSize, {
                                    class: this.options.className,
                                })
                                decorations.push(decoration)
                            }
                        })

                        return DecorationSet.create(doc, decorations)
                    },
                },
            }),
        ]
    }
}
