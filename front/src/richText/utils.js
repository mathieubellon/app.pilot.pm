/*
Utilities for tiptap
*/
import _ from "lodash"

/***********************
 * Coordinates  calculations
 ************************/

function getEmptyBoundingBox(left = 0, top = 0) {
    return {
        left: left,
        top: top,
        right: left,
        bottom: top,
        width: 0,
        height: 0,
    }
}

function translateBoundingRect(boundingRect, left, top) {
    return {
        left: boundingRect.left - left,
        top: boundingRect.top - top,
        right: boundingRect.right - left,
        bottom: boundingRect.bottom - top,
        width: boundingRect.width,
        height: boundingRect.height,
    }
}

/**
 * Get the x and y coordinates at the top center of the current DOM selection.
 */
function getRangeSelectionBoundingRect() {
    let range, rects
    // try/catch to handle
    // "IndexSizeError: Failed to execute 'getRangeAt' on 'Selection': 0 is not a valid index."
    try {
        range = window.getSelection().getRangeAt(0)
        rects = range.getClientRects()
    } catch (e) {
        return null
    }
    if (!rects.length) return range.getBoundingClientRect()
    let left, right, top, bottom
    for (let i = 0; i < rects.length; i++) {
        let rect = rects[i]
        if (left == right) {
            ;({ left, right, top, bottom } = rect)
        } else if (
            rect.top < bottom - 1 &&
            // Chrome bug where bogus rectangles are inserted at span boundaries
            (i == rects.length - 1 || Math.abs(rects[i + 1].left - rect.left) > 1)
        ) {
            left = Math.min(left, rect.left)
            right = Math.max(right, rect.right)
            top = Math.min(top, rect.top)
            bottom = Math.max(bottom, rect.bottom)
        }
    }
    return { left, top, right, bottom, width: right - left, height: bottom - top }
}

/**
 * Get the x and y coordinates of the current prosemirror non-Node selection,
 * positioned at the topmost position verticallly  and  at the horizontal center
 */
function getSelectionBoundingRect(editor) {
    let boundingRect = getRangeSelectionBoundingRect()
    if (boundingRect && boundingRect.top != 0) {
        return boundingRect
    }
    // Fallback on an empty bounding box at the coords
    let coords = editor.view.coordsAtPos(editor.state.selection.from)
    return getEmptyBoundingBox(coords.left, coords.top)
}

/**
 * Get the x and y coordinates of the current prosemirror Node selection,
 * positioned at the vertical center and to the leftmost position horizontally.
 */
function getNodeSelectionBoundingRect(editor) {
    let selected = editor.view.dom.querySelector(".ProseMirror-selectednode")
    if (selected) return selected.getBoundingClientRect()
    // No luck, bail out
    else return getEmptyBoundingBox()
}

/***********************
 * Prosemirror Document utils
 ************************/

/**
 * Returns the currently selected image, if applicable
 *
 * @param selection Prosemirror Selection
 * @returns Image Node or null
 */
function getSelectedImageNode(selection) {
    // Standard case
    let imageNode = selection.node
    if (imageNode && imageNode.type.name == "image") {
        return {
            imageNode: imageNode,
            imagePos: selection.anchor,
        }
    }
    if (selection.$anchor) {
        // Annotated image : the selection is on the overlay, we need to check the node before
        imageNode = selection.$anchor.nodeBefore
        if (selection.empty && imageNode && imageNode.type.name == "image") {
            return {
                imageNode: imageNode,
                imagePos: selection.anchor - 1,
            }
        }
    }
    // No image selected
    return {
        imageNode: null,
        imagePos: null,
    }
}

/**
 * Tells if an image is currently selected
 *
 * @param selection Prosemirror Selection
 * @returns {boolean} true if an image is currently selectd
 */
function isImageSelected(selection) {
    return getSelectedImageNode(selection).imageNode != null
}

/**
 * Tells if an empty Paragraph Node is currently selected
 *
 * @param selection Prosemirror Selection
 * @returns {boolean} true if an empty Paragraph Node is currently selected
 */
function isEmptyParagraphSelected(selection) {
    return (
        selection.$from.parent.content.size == 0 &&
        selection.$from.parent.type.name == "paragraph" &&
        selection.$head.depth == 1 &&
        selection.empty
    )
}

/**
 * Returns the start/end position of a link mark around the selection in a document
 *
 *  * @returns {
 *      linkMark: the active link mark, or undefined if there's no link at the current selection
 *      startPos: start position of the active link mark
 *      endPos: end position of the active link mark
 *  }
 */
function linkAroundSelection(editor) {
    let $pos = editor.state.selection.$from

    let marks = [...$pos.marks(), ...(editor.state.storedMarks || [])]
    let linkMark = marks.reduce((found, m) => found || (m.type.name == "link" && m), null)
    if (!linkMark) {
        return {}
    }

    let start = $pos.parent.childAfter($pos.parentOffset)
    if (!start.node) {
        return {}
    }

    let linkType = linkMark.type
    let startIndex = $pos.index()
    let startPos = $pos.start() + start.offset
    while (startIndex > 0 && linkType.isInSet($pos.parent.child(startIndex - 1).marks)) {
        startIndex -= 1
        startPos -= $pos.parent.child(startIndex).nodeSize
    }

    let endIndex = $pos.indexAfter()
    let endPos = startPos + start.node.nodeSize
    while (
        endIndex < $pos.parent.childCount &&
        linkType.isInSet($pos.parent.child(endIndex).marks)
    ) {
        endPos += $pos.parent.child(endIndex).nodeSize
        endIndex += 1
    }

    return { linkMark, startPos, endPos }
}

/**
 * Get all the heading nodes in a prosemirror document
 *
 * @param jsonDoc
 * @returns {[]}
 */
function getHeadingNodes(jsonDoc) {
    // Traverse the whole tree
    let headings = []
    traverseProsemirrorNode(jsonDoc, (node) => {
        if (node.type == "heading") headings.push(node)
    })
    return headings
}

/**
 * Given the heading node index in the document, returns its viewport coordinates,
 * relative to the current scroll position of the editor container.
 *
 * @param editor
 * @param headingIndex
 * @returns {{top: *, left: *, bottom: *, right: *}}
 */
function getHeadingCoords(editor, headingIndex) {
    let headingPos

    // Find the node corresponding to the chosen heading
    editor.state.doc.descendants((node, offset) => {
        if (node.type.name == "heading") {
            if (headingIndex == 0) {
                headingPos = offset
            }
            headingIndex--
        }
    })

    // Not found, weird, bail out
    if (!headingPos) return

    // Get the coords of thie heading node, relative to the current scroll position
    return editor.view.coordsAtPos(headingPos)
}

/***********************
 * Json Model utils
 ************************/

function serializeDocToHTML(editor, newLine = "") {
    return serializeNodeToHTML(editor.state.doc, editor.options.serializer, newLine)
}

function serializeNodeToHTML(node, serializer, newLine = "") {
    let serializedNodes = []
    node.content.forEach((childNode) => {
        serializedNodes.push(serializer.serializeNode(childNode).outerHTML)
    })
    let html = serializedNodes.join(newLine)
    // Ignore the document if it's composed of only one empty paragraphs
    if (html == "<p></p>") {
        html = ""
    }
    return html
}

/***********************
 * Serialization
 ************************/

function traverseProsemirrorNode(node, callback) {
    callback(node)
    if (_.isArray(node.content)) {
        for (let childNode of node.content) {
            traverseProsemirrorNode(childNode, callback)
        }
    }
}

/***********************
 * Exports
 ************************/

export {
    translateBoundingRect,
    getSelectionBoundingRect,
    getNodeSelectionBoundingRect,
    getEmptyBoundingBox,
    isImageSelected,
    getSelectedImageNode,
    isEmptyParagraphSelected,
    linkAroundSelection,
    getHeadingNodes,
    getHeadingCoords,
    serializeDocToHTML,
    serializeNodeToHTML,
    traverseProsemirrorNode,
}
