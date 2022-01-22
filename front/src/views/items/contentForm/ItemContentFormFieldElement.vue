<template>
<div
    class="ItemContentFormFieldElement"
    :class="{
        'is-warning': warnings && warnings.$invalid,
        'is-invalid': validation && validation.$invalid,
    }"
    :fieldName="schema.name"
>
    <div
        v-if="conflict"
        class="p-2 bg-purple-100 text-purple-900 border rounded border-purple-200"
    >
        <div class="text-black font-bold">{{ $t("conflict") }}</div>
        <div>
            {{ $t("otherUser") }} :
            <UserDisplay
                v-if="conflict.editor.id"
                :user="conflict.editor"
            />
            <template v-else>{{ conflict.editor }}</template>
        </div>
        <div class="mb-1">
            {{ $t("remoteValue") }} :
            <span class="font-bold">{{ conflict.value }}</span>
        </div>

        <button
            class="button is-white is-small border-purple-300 border rounded"
            @click="conflictAcceptMine(schema.name)"
        >
            {{ $t("acceptMine") }}
        </button>
        <button
            class="button is-white is-small border-purple-300 border rounded"
            @click="conflictAcceptTheirs(schema.name)"
        >
            {{ $t("acceptTheirs") }}
        </button>
    </div>

    <div class="form__field__label">
        <span class="flex items-center">
            <div class="mr-1">{{ label }}</div>
            <div
                v-if="schema.required"
                class="form__field__label__minitag"
            >
                {{ $t("required") }}
            </div>
        </span>

        <span class="flex items-center flex-shrink-0">
            <slot name="labelOptions" />
            <div
                v-if="realtimeUserActivity"
                class="flex items-center"
            >
                <span
                    v-for="user in realtimeUserActivity.updating"
                    class="rounded-full border border-gray-200"
                >
                    <div class="px-1 text-xs leading-tight flex items-center">
                        <Icon
                            class="h-4"
                            name="Edit"
                        />
                        {{ user.username }}
                    </div>
                </span>
            </div>
        </span>
    </div>

    <component
        ref="widget"
        :annotations="annotations"
        :is="widgetComponent"
        :schema="schema"
        :value="value"
        @annotations="onAnnotations"
        @input="updateValue"
        @selection="onSelection"
    />

    <div class="form__field__help">
        <div class="flex w-full">
            <div class="flex-1 flex-col">
                <div
                    v-if="helpText"
                    v-html="helpText"
                />
                <ValidationErrors
                    :showOnlyWhenDirty="false"
                    :validation="validation"
                />
                <ValidationWarnings
                    :showOnlyWhenDirty="false"
                    :warnings="warnings"
                />
            </div>
            <div class="flex flex-shrink-0">
                <div
                    v-if="schema.is_textual"
                    class="flex flex-shrink-0 px-1 flex items-center h-auto"
                    :class="{ 'text-yellow-900 bg-yellow-100 rounded-b': remainingChar < 0 }"
                >
                    <div
                        v-if="schema.max_length"
                        class="font-mono"
                    >
                        {{ characterLength }}/{{ schema.max_length }}
                    </div>
                    <div
                        v-else
                        class="font-mono"
                    >
                        {{ characterLength }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
</template>

<script>
/**
 *  WARNING : This component may be used inside the Item Detail view,
 *  but also inside the Item Add Form, which doest not have access to all
 *  the fancy item detail store data.
 *  Store access should be carefully checked.
 */

import _ from "lodash"
import $ from "jquery"
const twitter = require("twitter-text")
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"
import { translateItemFieldAttribute } from "@js/localize.js"
import realtime from "@js/realtime"
import { itemContentSchema } from "@richText/schema"
import PilotMixin from "@components/PilotMixin"

import CharInput from "@components/forms/widgets/CharInput"
import CharInputWrapping from "@components/forms/widgets/CharInputWrapping"
import TextInput from "@components/forms/widgets/TextInput"
import ItemContentRichEditor from "./widgets/ItemContentRichEditor"
import AssetWidget from "./widgets/AssetWidget"
import ChoiceInput from "@components/forms/widgets/ChoiceInput"
import RadioInput from "./widgets/RadioInput"
import MultiCheckboxesInput from "./widgets/MultiCheckboxesInput"
import AutoCompleteInput from "./widgets/AutoCompleteInput"
import HelpText from "./widgets/HelpText"
import FileInput from "./widgets/FileInput"

const widgetComponentMap = {
    char: CharInputWrapping,
    text: TextInput,
    prosemirror: ItemContentRichEditor,
    asset: AssetWidget,
    email: CharInput,
    integer: CharInput,
    choice: ChoiceInput,
    radio: RadioInput,
    multi_checkboxes: MultiCheckboxesInput,
    auto_complete: AutoCompleteInput,
    facebook: ItemContentRichEditor,
    twitter: ItemContentRichEditor,

    help_text: HelpText,

    file: FileInput,
}

export default {
    name: "ItemContentFormFieldElement",
    mixins: [PilotMixin],
    props: {
        schema: {
            type: Object,
            required: true,
        },
        value: {
            required: true,
        },
        validation: {
            required: true,
        },
        warnings: {
            required: true,
        },
    },
    computed: {
        ...mapState("itemContentForm", [
            "itemEditable",
            "pendingChanges",
            "conflictedFields",
            "desynchronized",
        ]),
        ...mapGetters("itemContentForm", ["realtimeUserActivites"]),
        widgetComponent() {
            return widgetComponentMap[this.schema.type]
        },
        realtimeUserActivity() {
            return this.realtimeUserActivites ? this.realtimeUserActivites[this.schema.name] : null
        },
        characterLength() {
            if (!this.value) {
                return 0
            }
            if (this.schema.is_prosemirror) {
                let text = itemContentSchema.textFromJSON(this.value)
                if (this.schema.type == "twitter") {
                    return twitter.getTweetLength(text)
                } else {
                    return text.length
                }
            } else {
                return this.value.length
            }
        },
        remainingChar() {
            return this.schema.max_length - this.characterLength
        },
        label() {
            return translateItemFieldAttribute(this.schema.label)
        },
        helpText() {
            // Special case for help text type, which have a distinct display managed in their widget
            if (this.schema.type == "help_text") {
                return null
            }
            // General case
            return translateItemFieldAttribute(this.schema.help_text)
        },
        annotations() {
            return _.get(this, "itemEditable.annotations") || {}
        },
        conflict() {
            return this.conflictedFields ? this.conflictedFields[this.schema.name] : null
        },
    },
    methods: {
        ...mapActions("itemContentForm", ["conflictAcceptMine", "conflictAcceptTheirs"]),
        updateValue(value) {
            let activity = {
                field_updating: this.schema.name,
            }
            realtime.updateUserActivity(activity)

            let fieldName = this.schema.name
            if (this.schema.is_prosemirror) {
                this.$emit("input", { ...value, fieldName })
            } else {
                this.$emit("input", { value, fieldName })
            }
        },
        onAnnotations(annotationsData) {
            annotationsData.fieldName = this.schema.name
            this.$emit("annotations", annotationsData)
        },
        onSelection(selection) {
            // Don't send selection update while we're updating,
            // because the cursor would jump.
            // Instead, the selection will be sent along with the field updates
            if (this.pendingChanges && !this.pendingChanges[this.schema.name]) {
                realtime.updateUserActivity({ selection })
            }
        },
    },
    mounted() {
        $(this.$el).on("focusin", () => {
            realtime.updateUserActivity({
                field_focus: this.schema.name,
            })
        })
        $(this.$el).on("focusout", () => {
            realtime.updateUserActivity({
                field_focus: null,
                field_updating: null,
                selection: null,
            })
        })
    },
    beforeDestroy() {
        $(this.$el).off("focusin")
        $(this.$el).off("focusout")
    },
    i18n: {
        messages: {
            fr: {
                acceptMine: "Conserver mon texte",
                acceptTheirs: "Utiliser son texte",
                cancel: "Annuler les modifications",
                characters: "Caractères",
                conflict:
                    "Conflit : un autre utilisateur a modifié ce champ en même temps que vous",
                otherUser: "Autre utilisateur",
                remainingChar: "reste {remainingChar}",
                remoteValue: "Son texte",
                contentSavedOrReady: "Contenu sauvegardé",
                saving: "Sauvegarde en cours",
            },
            en: {
                acceptMine: "Keep my text",
                acceptTheirs: "Accept his/her text",
                cancel: "Cancel changes",
                characters: "Characters",
                conflict: "Conflict : another user edited this field at the same time than you",
                otherUser: "Other user",
                remainingChar: "{remainingChar} remaining",
                remoteValue: "His/her text",
                contentSavedOrReady: "Content saved",
                saving: "Saving ...",
            },
        },
    },
}
</script>
