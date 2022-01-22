<template>
<div class="LabelForm">
    <FormField
        :schema="{
            type: 'char',
            label: $t('name'),
            placeholder: $t('name'),
        }"
        v-model.trim="labelModel.name"
        :vuelidate="$v.labelModel.name"
    />

    <div class="form__field">
        <div class="form__field__label mb-1">{{ $t("preview") }}</div>
        <span
            v-if="labelModel.name"
            class="Label"
            :style="style"
        >
            {{ labelModel.name }}
        </span>
    </div>

    <FormField
        v-model="localLabel"
        :schema="{
            type: 'color',
            label: $t('color'),
            inputType: 'all',
        }"
        :vuelidate="$v.labelModel.color"
    />
</div>
</template>

<script>
import { required } from "vuelidate/lib/validators"
import PilotMixin from "@components/PilotMixin"

import ColorPickerCurated from "@components/ColorPickerCurated"

export default {
    name: "LabelForm",
    mixins: [PilotMixin],
    components: {
        ColorPickerCurated,
    },
    props: {
        labelModel: Object,
    },
    computed: {
        style() {
            return {
                "background-color": this.labelModel.background_color,
                color: this.labelModel.color,
            }
        },
        localLabel: {
            get: function () {
                return {
                    color: this.labelModel.color,
                    backgroundColor: this.labelModel.background_color,
                }
            },
            set: function (newValue) {
                this.labelModel.background_color = newValue.backgroundColor
                this.labelModel.color = newValue.color
            },
        },
    },
    validations: {
        labelModel: {
            name: { required },
            color: { required },
        },
    },
    i18n: {
        messages: {
            fr: {
                preview: "Aperçu",
            },
            en: {
                preview: "Preview",
            },
        },
    },
}
</script>
