import $ from "jquery"
import { waitUntil } from "@js/utils"

/*
Decoration Boxes are displayed on the right of the prosemirror editor.
They are linked to some decorations into the document :
annotation, highlight for review change, annotation migration failure.

On screen too small to fit them on the right column, the annotation are displayed
on top of the prosemirror content, below the cursor
 */

const GUTTER_SIZE = 15
const FLOATING_VERTICAL_GUTTER_SIZE = 25
const FLOATING_MODE_BREAKPOINT = 1400

/**
 * Check if there's enough space to display the boxes on the right column.
 *
 * @returns {boolean} true if there's enough space for right column display
 */
function hasEnoughSpaceForColumnDisplay() {
    return $(".CenterPane").outerWidth() >= FLOATING_MODE_BREAKPOINT
}

/**
 * Return the right offset where the DecorationBoxesColumn should be positionned in floating mode
 */
function getRightOffsetFloating() {
    let totalMargin =
        $(".CenterPane").outerWidth() - $(".ContentFormContainer__FormAndColumns").outerWidth()
    let rightMargin = totalMargin / 2
    return Math.min(-rightMargin + GUTTER_SIZE, 0)
}

/**
 * Returns the relative top coordinate where the box should be positioned.
 * Take a starting absolute top position, then apply some offset by taking into account
 * current scroll, navbar and menus to align them.
 * If there's not enough space for right column display, apply an additionnal offset
 * because the boxes are displayed above prosemirror content
 *
 * @param absoluteStartingTopPos
 * @returns {number} relative top position
 */
function getTopPosition(topPosRelativeToPositionnedParent) {
    let contentForm = $(".ContentFormContainer__FormAndColumns")
    let contentFormOffset = contentForm.offset()
    let offsetTop = contentFormOffset ? contentFormOffset.top : 0
    let top =
        topPosRelativeToPositionnedParent - // position relative to app body
        offsetTop // adjust for app body offset

    let contentFormBottom = contentForm.height()
    let annotationHeight = $(".ItemDetailTextAnnotations").height()
    if (hasEnoughSpaceForColumnDisplay()) {
        // Don't go below the container bottom
        top = Math.min(top, contentFormBottom - annotationHeight)
    } else {
        // additionnal offset if the boxes are displayed above prosemirror content
        if (top < contentFormBottom - annotationHeight) {
            top += FLOATING_VERTICAL_GUTTER_SIZE
        } else {
            top -= annotationHeight
        }
    }

    // Don't go above the container top
    return Math.max(top, 0)
}

/**
 * Align the boxes top&right, depending on the space available.
 * When there's enough space for the column display, the boxes are positionned next to the prosemirror editor.
 * When there's not enough space, the boxes are stuck with the right border of the ItemDetailBody__middlepane.
 * This position may move as the window is resized, or when the right panels are opened.
 */
function alignBoxes(pmView) {
    // Prevent hidden prosemirror to align on topCoord 0
    if ($(pmView.dom.parentNode).is(":hidden")) {
        return
    }

    /**
     * Align right the DecorationBoxesColumn
     */
    if (hasEnoughSpaceForColumnDisplay()) {
        $(".ContentFormContainer__DecorationBoxesColumn").each((i, element) => {
            element.style.right = ""
        })
    } else {
        // Stick the annotation to the right of the CenterPane
        $(".ContentFormContainer__DecorationBoxesColumn").css("right", getRightOffsetFloating())
    }

    /**
     * Align top the ItemDetailTextAnnotations inside the DecorationBoxesColumn
     */
    let cursorPos = pmView.state.selection.from
    if (!cursorPos) cursorPos = 0
    let topCoord

    try {
        // Best try : Actual coordinates calculated by prosemirror
        let coords = pmView.coordsAtPos(cursorPos)
        topCoord = coords.top
    } catch (e) {
        try {
            // Fallback : pm view container top position
            topCoord = $(pmView.dom.parentNode).offset().top
        } catch (e) {
            // Total disaster : top of the page
            topCoord = 0
        }
    }

    waitUntil(
        () => $(".ItemDetailTextAnnotations").height() > 0,
        () => {
            $(".ItemDetailTextAnnotations").css("top", getTopPosition(topCoord))
        },
        200,
        2,
    )
}

export { getTopPosition, alignBoxes }
