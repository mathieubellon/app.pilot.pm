import _ from "lodash"
const twitter = require("twitter-text")
import { required, maxLength, minValue, maxValue, email, numeric } from "vuelidate/lib/validators"
import { req, withParams } from "vuelidate/lib/validators/common"

import { EMPTY_PROSEMIRROR_DOC, itemContentSchema } from "@richText/schema"

function prosemirrorRequired(value) {
    if (!value) {
        return false
    }
    return !_.isEqual(value, EMPTY_PROSEMIRROR_DOC)
}

function twitterMaxLength(maxLength) {
    return withParams(
        {
            type: "twitterMaxLength",
            maxLength: maxLength,
        },
        (value) => {
            return (
                !req(value) ||
                twitter.getTweetLength(itemContentSchema.textFromJSON(value)) <= maxLength
            )
        },
    )
}

function prosemirrorMaxLength(maxLength) {
    return withParams(
        {
            type: "prosemirrorMaxLength",
            maxLength: maxLength,
        },
        (value) => {
            return !req(value) || itemContentSchema.textFromJSON(value).length <= maxLength
        },
    )
}

function regexValidator(regex, errorMessage) {
    return withParams(
        {
            type: "regex",
            regex,
            errorMessage,
        },
        (value) => {
            return !req(value) || regex.test(value)
        },
    )
}

function createFieldValidation(fieldSchema) {
    let fieldValidation = {}
    if (fieldSchema.required) {
        fieldValidation.required = fieldSchema.is_prosemirror ? prosemirrorRequired : required
    }
    if (fieldSchema.max_length && fieldSchema.validate_max_length) {
        if (fieldSchema.is_twitter) {
            fieldValidation.twitterMaxLength = twitterMaxLength(fieldSchema.max_length)
        } else if (fieldSchema.is_prosemirror) {
            fieldValidation.prosemirrorMaxLength = prosemirrorMaxLength(fieldSchema.max_length)
        } else {
            fieldValidation.maxLength = maxLength(fieldSchema.max_length)
        }
    }
    if (fieldSchema.min_value) {
        fieldValidation.minValue = minValue(fieldSchema.min_value)
    }
    if (fieldSchema.max_value) {
        fieldValidation.maxValue = maxValue(fieldSchema.max_value)
    }
    if (fieldSchema.type == "email") {
        fieldValidation.email = email
    }
    if (fieldSchema.type == "integer") {
        fieldValidation.numeric = numeric
    }
    if (fieldSchema.regex) {
        fieldValidation.regex = regexValidator(
            new RegExp(fieldSchema.regex),
            fieldSchema.regex_error_message,
        )
    }
    return fieldValidation
}

function createFieldWarning(fieldSchema) {
    let fieldWarnings = {}
    if (fieldSchema.max_length && !fieldSchema.validate_max_length) {
        if (fieldSchema.is_prosemirror) {
            fieldWarnings.prosemirrorMaxLength = prosemirrorMaxLength(fieldSchema.max_length)
        } else {
            fieldWarnings.maxLength = maxLength(fieldSchema.max_length)
        }
    }
    return fieldWarnings
}

export { createFieldValidation, createFieldWarning }
