<template>
<div
    v-if="validation"
    class="form__field__error mr-1"
>
    <template v-if="!showOnlyWhenDirty || validation.$dirty">
        <div v-if="validation.required === false">
            {{ $t("requiredField") }}
        </div>
        <div v-if="validation.maxLength === false">
            {{ $t("contentTooLong") }}
        </div>
        <div v-if="validation.prosemirrorMaxLength === false">
            {{ $t("contentTooLong") }}
        </div>
        <div v-if="validation.twitterMaxLength === false">
            {{ $t("contentTooLong") }}. {{ $t("twitterOnlyAllow") }}
            {{ this.validation.$params.twitterMaxLength.maxLength }} signes
        </div>
        <div v-if="validation.email === false">
            {{ $t("invalidEmail") }}
        </div>
        <div v-if="validation.minValue === false">
            {{ $t("valueTooLow") }} (min {{ this.validation.$params.minValue.min }})
        </div>
        <div v-if="validation.maxValue === false">
            {{ $t("valueTooHigh") }} (max {{ this.validation.$params.maxValue.max }})
        </div>
        <div v-if="validation.numeric === false">
            {{ $t("valueMustBeNumber") }}
        </div>
        <div v-if="validation.regex === false">
            {{ this.validation.$params.regex.errorMessage }}
        </div>
    </template>

    <div
        v-if="validation.serverSide"
        v-html="formatError(validation.serverSide)"
    />
</div>
</template>

<script>
import { formatError } from "@js/errors"

export default {
    name: "ValidationErrors",
    props: {
        validation: Object,
        showOnlyWhenDirty: {
            type: Boolean,
            default: true,
        },
    },
    data: () => ({
        formatError,
    }),
    i18n: {
        messages: {
            fr: {
                channelType: "Type de canal",
                contentTooLong: "Contenu trop long",
                creation: "Créé le",
                invalidEmail: "Email invalide",
                requiredField: "Ce champ est obligatoire",
                twitterOnlyAllow: "Twitter autorise seulement",
                valueMustBeNumber: "Nombre obligatoire",
                valueTooHigh: "Valeur trop haute",
                valueTooLow: "Valeur trop basse",
            },
            en: {
                channelType: "Channel type",
                contentTooLong: "Content too long",
                creation: "Created on",
                invalidEmail: "Invalid email",
                requiredField: "This field is required",
                twitterOnlyAllow: "Twitter only allows",
                valueMustBeNumber: "Mandatory number",
                valueTooHigh: "Value too high",
                valueTooLow: "Value too low",
            },
        },
    },
}
</script>
