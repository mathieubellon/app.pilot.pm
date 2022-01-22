import Vue from "vue"
import VueI18n from "vue-i18n"
import moment from "moment"
import "moment/locale/fr"

import flatpickr from "flatpickr/dist/flatpickr.js"
import flatpickrL10n from "flatpickr/dist/l10n"

import filesize from "filesize/lib/filesize.js"

Vue.use(VueI18n)

const FILE_SIZE_SYMBOLS = {
    fr: { B: "o", KB: "Ko", MB: "Mo", GB: "Go", TB: "To", PB: "Po", EB: "Eo", ZB: "Zo", YB: "Yo" },
}
let humanFileSize

function setCurrentLocale(locale, vueRoot = null) {
    window.pilot.currentLocale = locale

    /**
     * Vue
     */
    Vue.config.lang = locale
    if (vueRoot) {
        vueRoot.$i18n.locale = locale
    }

    /**
     * Moment
     */
    moment.locale(locale)

    /**
     * Flatpickr
     */

    let flatpickrLocales = {
        fr: flatpickrL10n.fr,
        en: {},
    }
    flatpickr.localize(flatpickrLocales[locale]) // default locale for the whole app

    /**
     * File size
     */

    if (locale == "fr") {
        humanFileSize = filesize.partial({
            symbols: FILE_SIZE_SYMBOLS.fr,
            round: 0,
        })
    } else {
        // Default to the builtin trad, which is english
        humanFileSize = filesize.partial({
            round: 0,
        })
    }
}

// Init libraries locales with the initial current locale
setCurrentLocale(window.pilot.currentLocale)

/**
 * In itemType schemas,
 * String attributes may be either a plain String or a translation dict in the form :
 * {
 *    'fr': 'Titre'
 *    'en': 'Title'
 * }
 *
 * Determine the correct string to display depending on the currentLocale.
 * This apply to the following attributes : title, help_text, placeholder, choiceText
 */
function translateItemFieldAttribute(attribute) {
    if (!attribute) {
        return attribute
    }
    if (typeof attribute === "string") {
        return attribute
    }
    if (typeof attribute === "object") {
        return attribute[window.pilot.currentLocale]
    }
    throw Error("Attribute must be a string or a translation object")
}

export { setCurrentLocale, translateItemFieldAttribute, humanFileSize }
