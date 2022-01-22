import _ from "lodash"

const keyCodes = {
    BACKSPACE: 8,
    TAB: 9,
    ENTER: 13,
    ESCAPE: 27,
    ARROW_LEFT: 37,
    ARROW_UP: 38,
    ARROW_RIGHT: 39,
    ARROW_DOWN: 40,
    DELETE: 46,
}

/**
 * A rudimentary random id generator
 *
 * @returns {string} random id
 */
function getRandomId() {
    // Convert the random int to a string
    return Math.floor(Math.random() * 0xffffffff) + ""
}

/**
 * Normalize any unicode string so it contains only ASCII characters.
 */
function toAlpha(value) {
    if (value) {
        return _.toString(value)
            .normalize("NFKD")
            .replace(/[\u0300-\u036f]/g, "")
    }
    return ""
}

/**
 * Normalize any unicode string so it contains only ASCII characters, and convert to lower case
 */
function toLowerAlpha(value) {
    return toAlpha(value).toLowerCase()
}

/**
 * Same than lodash sortBy function, but use a normalized alpha string
 */
function sortByAlphaString(collection, iteratees) {
    return _.sortBy(collection, (i) => toLowerAlpha(iteratees(i)))
}

/**
 * Tell if a string/character is comprised only of whitespaces
 */
function isSpace(string) {
    return _.isString(string) ? string.trim() === "" : undefined
}

/**
 *  Wait until the condition is met to trigger the action.
 *  Both `condition` and `action` should be callback with no parameters.
 *  Check every `ìnterval` milliseconds, for a maximum of `timeout` milliseconds
 */
function waitUntil(condition, action, timeout = 1000, interval = 50) {
    let intervalId = setInterval(() => {
        if (condition()) {
            clearInterval(intervalId)
            action()
        }
        timeout -= interval
        if (timeout <= 0) {
            clearInterval(intervalId)
        }
    }, interval)
}

export { keyCodes, getRandomId, toAlpha, toLowerAlpha, sortByAlphaString, isSpace, waitUntil }
