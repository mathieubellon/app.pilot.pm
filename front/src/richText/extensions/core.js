import _ from "lodash"
import { Bold as TiptapBold, Italic as TiptapItalic, Link as TiptapLink } from "tiptap-extensions"
import { Node, Plugin } from "tiptap"
import { getMarkAttrs } from "tiptap-utils"
import { getSelectedImageNode } from "@/richText/utils"

// We override the name to stay backward compatible with the old prosemirror schema
export class Bold extends TiptapBold {
    get name() {
        return "strong"
    }

    // Override tiptap default pasteRules because we don't want to overly interpret
    // underscores and stars in pasted text
    pasteRules() {
        return []
    }
}

// We override the name to stay backward compatible with the old prosemirror schema
export class Italic extends TiptapItalic {
    get name() {
        return "em"
    }

    // Override tiptap default pasteRules because we don't want to overly interpret
    // underscores and stars in pasted text
    pasteRules() {
        return []
    }
}

export class Link extends TiptapLink {
    get schema() {
        return {
            attrs: {
                href: {
                    default: null,
                },
                title: {
                    default: null,
                },
            },
            inclusive: false,
            parseDOM: [
                {
                    tag: "a[href]",
                    getAttrs: (dom) => ({
                        href: dom.getAttribute("href"),
                        title: dom.getAttribute("title"),
                    }),
                },
            ],
            toDOM: (node) => [
                "a",
                {
                    href: node.attrs.href,
                    title: node.attrs.title,
                    rel: "noopener noreferrer nofollow",
                },
                0,
            ],
        }
    }

    get plugins() {
        return [
            new Plugin({
                props: {
                    handleClickOn(view, pos, node, nodePos, event) {
                        const { schema } = view.state
                        const attrs = getMarkAttrs(view.state, schema.marks.link)

                        if (attrs.href && event.target instanceof HTMLAnchorElement) {
                            // We should not follow the link, instead we'll open a tooltip in TiptapMenu
                            event.stopPropagation()
                        }
                    },
                },
            }),
        ]
    }
}

export class Image extends Node {
    get name() {
        return "image"
    }

    get schema() {
        return {
            inline: true,
            attrs: {
                src: {},
                caption: {
                    default: null,
                },
                title: {
                    default: null,
                },
                alt: {
                    default: null,
                },
                alignment: {
                    default: null,
                },
            },
            group: "inline",
            draggable: true,
            parseDOM: [
                // The "figure" rule does not seems to work :-(
                {
                    tag: "figure",
                    priority: 51,
                    getAttrs(dom) {
                        let attrs = {}
                        let imageElement = dom.querySelector("img")
                        let captionElement = dom.querySelector("figcaption")

                        if (imageElement) {
                            attrs = {
                                src: imageElement.getAttribute("src"),
                                title: imageElement.getAttribute("title"),
                                alt: imageElement.getAttribute("alt"),
                            }
                        }

                        if (captionElement) {
                            attrs.caption = captionElement.textContent
                        }

                        return attrs
                    },
                },
                {
                    tag: "img[src]",
                    priority: 50,
                    getAttrs: (dom) => ({
                        src: dom.getAttribute("src"),
                        title: dom.getAttribute("title"),
                        alt: dom.getAttribute("alt"),
                    }),
                },
            ],
            toDOM(node) {
                let imageAttrs = _.pick(node.attrs, ["src", "title", "alt"])

                let surroundingAttrs = {}
                if (node.attrs.alignment) {
                    imageAttrs["style"] = "display: inline-block;"
                    surroundingAttrs["style"] = `text-align: ${node.attrs.alignment};`
                }

                if (node.attrs.caption) {
                    return [
                        "figure",
                        surroundingAttrs,
                        ["img", imageAttrs],
                        ["figcaption", node.attrs.caption],
                    ]
                } else {
                    if (node.attrs.alignment) {
                        return ["div", surroundingAttrs, ["img", imageAttrs]]
                    } else {
                        return ["img", imageAttrs]
                    }
                }
            },
        }
    }

    // We override the command so we can replace/update an existing image,
    // in addition to a plain creation.
    commands({ type }) {
        return (attrs) => (state, dispatch) => {
            let selection = state.selection
            let { imageNode, imagePos } = getSelectedImageNode(selection)
            // Replace an existing image node
            if (imageNode) {
                dispatch(state.tr.replaceRangeWith(imagePos, imagePos + 1, type.create(attrs)))
            }
            // Create an image node
            else {
                dispatch(
                    state.tr.insert(
                        selection.$cursor ? selection.$cursor.pos : selection.$to.pos,
                        type.create(attrs),
                    ),
                )
            }
        }
    }
}
