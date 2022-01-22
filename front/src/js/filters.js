import moment from "moment"
import Vue from "vue"
import i18n from "@js/i18n"

export function defaultVal(value, defaultValue) {
    return value ? value : defaultValue
}

export function dateFormat(value, format = "DD/MM/YY") {
    let momentDate = moment(value)
    if (!momentDate.isValid()) return value
    return momentDate.format(format)
}

export function dateTimeFormat(value) {
    return dateFormat(value, "DD/MM/YYYY HH:mm")
}

export function dateTimeFormatShort(value) {
    return dateFormat(value, "DD/MM/YY HH:mm")
}

export function timeAgo(value) {
    let momentDate = moment(value)
    if (!momentDate.isValid()) return value
    return momentDate.fromNow()
}

export function yesno(value) {
    return value ? i18n.t("yes") : i18n.t("no")
}

export function linebreaks(value) {
    return value.replace(/\n/g, "<br />")
}

export function installVueFilters() {
    Vue.filter("defaultVal", defaultVal)
    Vue.filter("dateFormat", dateFormat)
    Vue.filter("dateTimeFormat", dateTimeFormat)
    Vue.filter("dateTimeFormatShort", dateTimeFormatShort)
    Vue.filter("timeAgo", timeAgo)
    Vue.filter("yesno", yesno)
    Vue.filter("linebreaks", linebreaks)
    Vue.filter("firstLetter", firstLetter)
}

export function firstLetter(value) {
    if (!value) return ""
    return value.toString().charAt(0)
}
