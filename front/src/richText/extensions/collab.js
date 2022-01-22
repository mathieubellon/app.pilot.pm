import $ from "jquery"
import { Extension, Plugin, PluginKey } from "tiptap"
import { Step } from "prosemirror-transform"
import { Decoration, DecorationSet } from "prosemirror-view"
import { collab, receiveTransaction } from "prosemirror-collab"

const cursorKey = new PluginKey("cursors")

import $monitoring from "@js/monitoring"

function createCursorsPlugin(currentUserId) {
    return new Plugin({
        key: cursorKey,

        state: {
            init: (config) => ({
                cursorDecorations: DecorationSet.empty,
            }),
            apply: function (transaction, prev, state) {
                let action = transaction.getMeta(cursorKey) || {}

                if (action.type != "cursors") {
                    return prev
                }

                let decorations = []
                for (let user of action.users || []) {
                    // Don't decorate for our own user; or if no selection is set
                    if (user.id == currentUserId || !user.selection) {
                        continue
                    }

                    let { selection, color } = user
                    let { from, to } = selection

                    if (from == to) {
                        decorations.push(
                            Decoration.widget(
                                from,
                                $(
                                    `<span class="cursor" style="background-color: ${color}"></span>`,
                                )[0],
                            ),
                        )
                    } else {
                        decorations.push(
                            Decoration.inline(selection.from, selection.to, {
                                style: "background-color: " + color,
                            }),
                        )
                    }
                }

                return {
                    cursorDecorations: DecorationSet.create(state.doc, decorations),
                }
            },
        },

        props: {
            decorations(state) {
                return this.getState(state).cursorDecorations
            },
        },
    })
}

export class Collab extends Extension {
    get name() {
        return "Collab"
    }

    get defaultOptions() {
        return {
            userId: 0,
            clientId: 0,
            receiveSteps: ({ steps, clientId }) => {
                const { state, view, schema } = this.editor

                try {
                    let transaction = receiveTransaction(
                        state,
                        steps.map((step) => Step.fromJSON(schema, step)),
                        steps.map(() => clientId),
                        { mapSelectionBackward: true },
                    )

                    this.editor.dispatchTransaction(transaction)
                } catch (error) {
                    $monitoring.captureException(error, {
                        message: "Error when receiving a remote prosemirror transaction",
                        remoteClientId: clientId,
                        clientId: this.options.clientId,
                        userId: this.options.userId,
                    })

                    throw error
                }
            },
            updateCursors: (users) => {
                const { state, view } = this.editor
                view.dispatch(
                    state.tr.setMeta(cursorKey, {
                        type: "cursors",
                        users: users,
                    }),
                )
            },
        }
    }

    get plugins() {
        return [
            collab({
                clientID: this.options.clientId,
            }),
            createCursorsPlugin(this.options.userId),
        ]
    }
}
