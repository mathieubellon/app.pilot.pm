import _ from "lodash"
import moment from "moment"

function parseQueryString(str) {
    if (typeof str !== "string") {
        return {}
    }

    str = str.trim().replace(/^(\?|#|&)/, "")

    if (!str) {
        return {}
    }
    var qd = {}
    str.split("&").forEach(function (item) {
        var s = item.split("="),
            k = s[0],
            v = s[1] && decodeURIComponent(s[1])
        // sane check if we do not pass a "project=" query parameter
        if (v) {
            //(k in qd) ? qd[k].push(v) : qd[k] = [v]
            ;(qd[k] = qd[k] || []).push(v) //short-circuit
        }
    })
    return qd
}

function serializeForQueryString(value) {
    if (_.isDate(value) || moment.isMoment(value)) {
        return moment(value).format(API_DATE_FORMAT)
    }
    return value
}

const API_DATE_FORMAT = "YYYY-MM-DD"
class QueryParamSerializer {
    constructor(params = {}) {
        this.params = {}

        if (_.isString(params)) {
            this.setFromQueryString(params)
        } else if (_.isPlainObject(params)) {
            this.setFromObject(params)
        }
    }
    clear() {
        this.params = {}
    }
    setFromObject(params = {}) {
        _.forEach(params, (value, name) => this.setParam(name, value))
    }
    setFromQueryString(queryString) {
        this.params = parseQueryString(queryString)
    }
    addParam(name, value) {
        let paramsList = this.params[name]
        if (paramsList) paramsList.push(value)
        else this.params[name] = [value]
    }
    setParam(name, value) {
        if (_.isArray(value)) this.params[name] = value
        else this.params[name] = [value]
    }
    removeParam(name) {
        delete this.params[name]
    }
    addFromBigFilter(filterItems) {
        for (let filterItem of filterItems) {
            this.addParam(filterItem.name, filterItem.value)
        }
    }
    getQueryString() {
        let parts = []
        // Do a predictable iteration order by sorting the keys
        // This is useful to compare accurately query string between them
        for (let name of Object.keys(this.params).sort()) {
            for (let value of this.params[name]) {
                parts.push(
                    encodeURIComponent(name) +
                        "=" +
                        encodeURIComponent(serializeForQueryString(value)),
                )
            }
        }
        return parts.join("&")
    }
    // URLSearchParams is not defined on IE11 , this method is worthless while we must support it :-(
    getURLSearchParams() {
        return new URLSearchParams(this.getQueryString())
    }
}

export { parseQueryString, serializeForQueryString, QueryParamSerializer }
