import _ from "lodash"
import i18n from "@js/i18n"

function formatErrorList(errorList) {
    return errorList.join("<br />")
}

/**
 * Format an error dict send back by the API to be human-readable,
 * possibly recursively when there is nested error dicts inside
 */
function formatErrorDict(errorDict) {
    return _.map(errorDict, (error, key) => {
        if (_.isArray(error)) {
            error = formatErrorList(error)
        } else if (_.isObject(error)) {
            error = formatErrorDict(error)
        }

        if (key == "__all__" || key == "detail" || key == "non_field_errors") return error
        else return key + ": " + error
    }).join("<br />")
}

function formatError(error) {
    if (error.detail) {
        return error.detail
    } else if (_.isString(error)) {
        // This is a full HTML content, not really interesting to display to the user
        if (error.indexOf("<!DOCTYPE html>") > -1) {
            return i18n.t("internalError")
        }
        // This should be a human-readable message
        else {
            return error
        }
    } else if (_.isArray(error)) {
        // Human-readable message
        return formatErrorList(error)
    } else if (_.isObject(error)) {
        // Human-readable message
        return formatErrorDict(error)
    }

    return error
}

function getAxiosErrorMessage(axiosError) {
    if (!axiosError) return ""

    let response = axiosError.response

    if (response) {
        let error = response.data
        if (error) {
            return formatError(error)
        }
        return response
    }
    return axiosError + ""
}

export { formatError, formatErrorDict, getAxiosErrorMessage }
