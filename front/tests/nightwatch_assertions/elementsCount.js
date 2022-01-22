import * as util from "util"

export function assertion(selector, expectedCount, msg) {
    this.message =
        msg || util.format('Testing if there is %d elements matching "%s"', expectedCount, selector)

    this.expected = () => expectedCount

    this.pass = function (value) {
        return value == expectedCount
    }

    this.command = (callback) => {
        return this.api.elements("css selector", selector, callback)
    }

    this.value = (result) => {
        return result.value.length
    }
}
