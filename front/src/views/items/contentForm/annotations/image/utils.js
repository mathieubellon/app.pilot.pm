/**
 * Computes the absolute top/left offset of a DOM element relative to the document.
 * @param {Element} el the DOM element
 * @return {Object} an object containing the offset { top, left }
 */
function getOffset(el) {
    let _x = 0
    let _y = 0

    while (el && !isNaN(el.offsetLeft) && !isNaN(el.offsetTop)) {
        _x += el.offsetLeft - el.scrollLeft
        _y += el.offsetTop - el.scrollTop
        el = el.offsetParent
    }
    return { top: _y, left: _x }
}

/**
 * To get screen coordinates while taking into consideration mobile and the offset of the screen
 * @param {Object} event the DOM Event object
 * @param {Element} parent the parent element that triggers the event
 */
export function sanitizeCoordinates(event, parent) {
    let points = false

    if ((!event.offsetX || !event.offsetY) && event.event_ && event.event_.changedTouches) {
        points = {
            x: event.event_.changedTouches[0].clientX - getOffset(parent).left,
            y: event.event_.changedTouches[0].clientY - getOffset(parent).top,
        }
    } else {
        points = {
            x: event.offsetX,
            y: event.offsetY,
        }
    }

    return points
}
