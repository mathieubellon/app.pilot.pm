<template>
<div :class="inputStylingClass">
    <!--
    We'll need an editor component whatever the mode :
    Non-diff mode ==> old version display. We need an editor component to show the annotations
    Diff mode ==> We need an editor component to show the diff
    -->
    <ItemContentRichEditor
        v-if="fieldSchema.is_prosemirror"
        :annotations="annotations"
        :readOnly="true"
        :schema="fieldSchema"
        :value="formattedValue"
    />

    <div v-else-if="fieldSchema.type == 'asset' && formattedValue">
        <!-- this v-if on formattedValue.size is used when quitting diffing mode,
        because the formattedValue stay a string for a short period of time
        before the Vue reactivity kick in and recompute it -->
        <template v-if="formattedValue.size">
            <div v-if="hasWorkingImages">
                <div v-for="(workingImageUrl, index) in formattedValue.working_urls">
                    <AnnotatableImage
                        :annotations="annotations"
                        :annotationsKey="`${fieldSchema.name}-${index}`"
                        :readOnly="true"
                        :src="workingImageUrl"
                    />
                    <br />
                </div>
            </div>

            <AssetPreview
                v-else
                :asset="formattedValue"
                context="itemMedia"
            />

            {{ $t("downloadOriginal", { size: humanFileSize(formattedValue.size) }) }} :
            <a :href="formattedValue.file_url">{{ formattedValue.name }}</a>
        </template>
    </div>

    <!--
    We need html for those cases :
     - For TextFields, we need an html rendering to convert the \n into <br /> and display them correctly
     - For Choices, we need an html rendering to display correctly the <br />
     - HelpText are rendered as html content
    -->
    <div
        v-else
        v-html="formattedValue"
    />
</div>
</template>

<script>
import _ from "lodash"
import { humanFileSize } from "@js/localize"

import { translateItemFieldAttribute } from "@js/localize"
import { EMPTY_PROSEMIRROR_DOC } from "@richText/schema"

import ItemContentRichEditor from "./widgets/ItemContentRichEditor"
import AssetPreview from "@views/assets/AssetPreview.vue"
import AnnotatableImage from "./annotations/image/AnnotatableImage.vue"

export default {
    name: "ItemContentFieldReadOnly",
    components: {
        ItemContentRichEditor,
        AssetPreview,
        AnnotatableImage,
    },
    props: {
        value: {},
        fieldSchema: Object,
        annotations: Object,
    },
    data: () => ({ humanFileSize }),
    computed: {
        formattedValue() {
            return this.formatReadOnlyValue(this.value)
        },
        hasWorkingImages() {
            let asset = this.value
            return (
                asset &&
                (asset.filetype === "image" || asset.filetype === "pdf") &&
                asset.working_urls &&
                asset.working_urls.length > 0
            )
        },
        inputStylingClass() {
            if (this.fieldSchema.is_prosemirror) {
                return ""
            } else if (this.fieldSchema.type == "help_text") {
                return "ItemContentHelpText"
            } else {
                return "InputStyling"
            }
        },
    },
    methods: {
        formatReadOnlyValue(value) {
            if (this.fieldSchema.type == "help_text") {
                return this.fieldSchema.help_text
            }

            if (!value) {
                return this.fieldSchema.is_prosemirror ? EMPTY_PROSEMIRROR_DOC : value
            }

            if (this.fieldSchema.type == "text") {
                return value.replace(/\n/g, "<br />")
            }

            if (this.fieldSchema.choices) {
                let result = []

                let selectedChoices = value
                if (!_.isArray(selectedChoices)) {
                    selectedChoices = [selectedChoices]
                }

                let choicesMap = _.fromPairs(this.fieldSchema.choices)
                for (let selectedChoice of selectedChoices) {
                    let choiceLabel = choicesMap[selectedChoice]
                    if (choiceLabel) {
                        result.push(translateItemFieldAttribute(choiceLabel))
                    }
                }
                return result.length == 0 ? "" : result.join("<br />")
            }

            return value
        },
    },
    i18n: {
        messages: {
            fr: {
                downloadOriginal: "Télécharger l'original ({size})",
            },
            en: {
                downloadOriginal: "Download the original ({size})",
            },
        },
    },
}
</script>
