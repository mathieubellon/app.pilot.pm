import { Slice, Fragment } from "prosemirror-model"

function isEmptyNode(node) {
    // Only paragraph nodes can be cleaned
    if (node.type.name != "paragraph") return false

    // If there's no content property, the paragraph is empty and should be cleaned
    if (!node.content) return true

    // If all child nodes are hard_break or text full of spacing,
    // the paragraph is considered empty and should be cleaned
    // We clean the paragraph if we cannot find something else than a hard_break
    let onlySpacing = true
    node.content.forEach((node) => {
        // It's a text node, but without any character that's not a spacing ==> not empty
        if (node.type.name == "text" && node.textContent.match(/[^\s]/)) {
            onlySpacing = false
        }

        // It's anything else than a hard_break or a text node ==> not empty
        if (node.type.name != "hard_break" && node.type.name != "text") {
            onlySpacing = false
        }
    })
    return onlySpacing
}

function removeEmptyParagraphsFromSlice(slice) {
    let nonEmptyNodes = []
    for (let i = 0; i < slice.content.childCount; i++) {
        let node = slice.content.child(i)
        if (!isEmptyNode(node)) {
            nonEmptyNodes.push(node)
        }
    }
    return new Slice(Fragment.from(nonEmptyNodes), slice.openStart, slice.openEnd)
}

function getEmptyParagraphPositions(content) {
    // content is a Fragment instance
    let positions = []
    content.forEach((node, position, index) => {
        if (isEmptyNode(node)) {
            positions.push({
                from: position,
                to: position + node.nodeSize,
                index: index,
            })
        }
    })
    return positions
}

function cleanEmptyParagraphs(editor) {
    // The full doc content (a Fragment instance)
    let content = editor.state.doc.content
    // Get the positions of all the empty paragraphs
    let emptyParagraphPositions = getEmptyParagraphPositions(content)
    // This line is CRITICAL : we need to apply the deletion from the end of the document.
    // Because the transaction steps are sequential, the position are updated between each steps.
    // If we start from the beggining, the nodes after the first would move closer to the beggining
    // of the content, but we don't update their position between each transaction step.
    // An elegant solution is simply to start from the end of the content by reversing this array.
    emptyParagraphPositions.reverse()
    // Create a transaction to cut all the empty nodes
    let transaction = editor.state.tr
    // Apply the empty paragraph removals
    for (let position of emptyParagraphPositions) {
        transaction.delete(position.from, position.to)
    }
    // Dispatch this transaction
    editor.dispatchTransaction(transaction)
}

export { cleanEmptyParagraphs, removeEmptyParagraphsFromSlice }
