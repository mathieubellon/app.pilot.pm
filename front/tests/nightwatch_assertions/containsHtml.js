/**
 * Checks if the given element contains the specified html.
 *
 * ```
 *    this.demoTest = function (client) {
 *      browser.assert.containsHtml('#main', '<strong>The Night Watch</strong>');
 *    };
 * ```
 *
 * @method containsHtml
 * @param {string} selector The selector (CSS / Xpath) used to locate the element.
 * @param {string} expectedHtml The html to look for.
 * @param {string} [message] Optional log message to display in the output. If missing, one is displayed by default.
 * @api assertions
 */

import * as util from "util"

export function assertion(selector, expectedHtml, msg) {
    var MSG_ELEMENT_NOT_FOUND =
        'Testing if element <%s> contains html: "%s". ' + "Element could not be located."

    this.message =
        msg || util.format('Testing if element <%s> contains html: "%s".', selector, expectedHtml)

    this.expected = function () {
        return expectedHtml
    }

    this.pass = function (value) {
        return value.indexOf(expectedHtml) > -1
    }

    this.failure = function (result) {
        var failed = result === false || (result && result.status === -1)
        if (failed) {
            this.message = msg || util.format(MSG_ELEMENT_NOT_FOUND, selector, expectedHtml)
        }
        return failed
    }

    this.value = function (result) {
        return result.value
    }

    this.command = function (callback) {
        return this.api.execute(
            function (selector) {
                return $(selector).html()
            },
            [selector],
            callback,
        )
    }
}
