<template>
<Popper
    position="auto"
    triggerElementName="RealTimeValidation"
    triggerType="click"
>
    <template #triggerElement>
        <button
            class="button"
            :class="{
                'is-red': hasAnyError,
                'is-yellow': hasAnyWarning,
            }"
            ref="RealTimeValidation"
            type="button"
        >
            <template v-if="hasAnyError">
                {{ $t("invalidForm") }}
            </template>
            <template v-else-if="hasAnyWarning">
                {{ $t("warningForm") }}
            </template>
            <template v-else>
                {{ $t("toc") }}
            </template>
            <!-- The empty span is required to correctly align with flex display -->
            <span>
                <Icon
                    class="caret"
                    :class="{
                        'text-white': hasAnyError,
                    }"
                    name="ChevronDown"
                />
            </span>
        </button>
    </template>

    <template #content>
        <div class="flex flex-col justify-start w-full max-h-screen overflow-y-auto">
            <div
                v-if="hasAnyError"
                class="text-base text-red-600 my-1 max-w-md leading-none mb-4"
            >
                {{ $tc("invalidFields", errorCount, { errorCount: errorCount }) }}
            </div>
            <div
                v-else
                class="text-sm font-medium leading-8 text-cool-gray-700"
            >
                {{ $t("tableOfContent") }}
            </div>
            <ItemTableOfContentsElement
                v-for="fieldSchema in allFieldSchemas"
                :fieldSchema="fieldSchema"
                :key="fieldSchema.name"
            />
        </div>
    </template>
</Popper>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import ItemTableOfContentsElement from "./ItemTableOfContentsElement"

const TOC_STATES = {
    Normal: "Normal",
    Warning: "Warning",
    Error: "Error",
}

export default {
    name: "ItemTableOfContents",
    mixins: [PilotMixin],
    components: {
        ItemTableOfContentsElement,
    },
    computed: {
        ...mapState("itemContentForm", ["item", "validation", "warnings"]),
        ...mapGetters("itemContentForm", ["allFieldSchemas"]),
        state() {
            if (this.validation && this.validation.$invalid) {
                return TOC_STATES.Error
            }
            if (this.warnings && this.warnings.$invalid) {
                return TOC_STATES.Warning
            }
            return TOC_STATES.Normal
        },
        hasAnyError() {
            return this.state == TOC_STATES.Error
        },
        hasAnyWarning() {
            return this.state == TOC_STATES.Warning
        },
        errorCount() {
            return this.validation
                ? _.filter(this.validation.content, (vuelidate) => vuelidate.$invalid).length
                : false
        },
    },
    i18n: {
        messages: {
            fr: {
                formIsInvalid:
                    "Ce contenu n'est pas valide. Certains champs du formulaire ne correspondent pas aux critères obligatoires demandés (nombre de caractères, saisie obligatoire etc..)",
                hasServerValidationError:
                    "Formulaire invalide: certains champs obligatoires ne sont pas correctement renseignés",
                invalidFields:
                    "Un champ n'est pas correctement renseigné | {errorCount} champs ne sont pas correctement renseignés",
                invalidForm: "Invalide",
                toc: "T.d.M",
                tableOfContent: "Table des matières",
                warningForm: "Ce contenu a des alertes",
            },
            en: {
                formIsInvalid:
                    "Some fields of the form do not correspond to the mandatory criteria requested (number of characters, mandatory entry etc...)",
                hasValidationError: "Validation error. Check your content",
                invalidFields:
                    "A field is not correctly filled in | {errorCount} fields are not correctly filled in",
                invalidForm: "This content is not valid",
                toc: "Table of Content",
                tableOfContent: "Table of Content",
                warningForm: "This content has warnings",
            },
        },
    },
}
</script>
