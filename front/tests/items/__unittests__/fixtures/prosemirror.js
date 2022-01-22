const EMPTY_PROSEMIRROR_DOC = { content: [{ type: "paragraph" }], type: "doc" }

function getProsemirrorContent(text) {
    return {
        content: [{ content: [{ text: text, type: "text" }], type: "paragraph" }],
        type: "doc",
    }
}

export { EMPTY_PROSEMIRROR_DOC, getProsemirrorContent }
