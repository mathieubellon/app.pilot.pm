import * as util from "util"
import _ from "lodash"

export function assertion(itemId, fieldName, expectedValue, msg) {
    this.message =
        msg || util.format("Testing if item #%d json_content match %s", itemId, expectedValue)

    this.expected = () => expectedValue

    this.pass = function (value) {
        let result = _.isEqual(value, expectedValue)
        // Print the json representation, instead of [object Object], to help debug errors
        if (!result) {
            console.error("====== DEBUG Assertion itemContentEquals =====")
            console.error("expected value", JSON.stringify(expectedValue))
            console.error("actual value", JSON.stringify(value))
            console.error("====== DEBUG END =====")
        }
        return result
    }

    this.command = (callback) => {
        return this.api.queryDb(
            "SELECT json_content FROM items_item WHERE id=" + itemId,
            (pgResponse, done) => {
                let item = pgResponse.rows[0]
                callback(item.json_content[fieldName])
                done()
            },
        )
    }

    this.value = (result) => {
        return result
    }
}
