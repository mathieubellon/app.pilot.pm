<template>
<div class="form__field">
    <template v-if="schema.component">
        <div class="form__field__label">{{ schema.label }}</div>
        <component
            :class="{ 'is-invalid': vuelidate && (vuelidate.$error || vuelidate.serverSide) }"
            :is="schema.component"
            :schema="schema"
            :value="value"
            @input="onInput"
        />
    </template>

    <!-- We must not use <label> around a RichTextInput because the MenuBar takes the focus instead of the editing area -->
    <template v-else-if="schema.type == 'richText'">
        <div class="form__field__label">{{ schema.label }}</div>
        <RichTextInput
            :editorSchema="schema.editorSchema"
            :value="value"
            @input="onInput"
        />
    </template>

    <!-- We must also avoid <label> around VueSelect -->
    <template v-else-if="schema.type == 'choice'">
        <div class="form__field__label">{{ schema.label }}</div>
        <component
            :class="{ 'is-invalid': vuelidate && (vuelidate.$error || vuelidate.serverSide) }"
            :is="widgetComponent"
            :schema="schema"
            :value="value"
            @input="onInput"
        />
    </template>

    <label v-else>
        <div
            v-if="schema.type != 'checkbox' && schema.type != 'toggle'"
            class="form__field__label"
        >
            {{ schema.label }}
        </div>
        <component
            :class="{ 'is-invalid': vuelidate && (vuelidate.$error || vuelidate.serverSide) }"
            :is="widgetComponent"
            :schema="schema"
            :value="value"
            @input="onInput"
        />
        <span v-if="schema.type == 'checkbox' || schema.type == 'toggle'">{{ schema.label }}</span>
    </label>

    <div
        v-if="schema.help_text"
        class="form__field__help"
    >
        {{ schema.help_text }}
    </div>

    <ValidationErrors :validation="vuelidate" />
</div>
</template>

<script>
import ValidationErrors from "@components/forms/ValidationErrors.vue"

import CharInputWrapping from "./widgets/CharInputWrapping"
import CharInput from "./widgets/CharInput"
import TextInput from "./widgets/TextInput"
import CheckboxInput from "./widgets/CheckboxInput"
import ChoiceInput from "./widgets/ChoiceInput"
import ColorInput from "./widgets/ColorInput"
import RichTextInput from "./widgets/RichTextInput"
import PasswordInput from "./widgets/PasswordInput"
import ToggleInput from "./widgets/ToggleInput"
import DatePickerInput from "./widgets/DatePickerInput"

const widgetComponentMap = {
    char: CharInputWrapping,
    email: CharInput,
    text: TextInput,
    checkbox: CheckboxInput,
    choice: ChoiceInput,
    color: ColorInput,
    richText: RichTextInput,
    password: PasswordInput,
    toggle: ToggleInput,
    date: DatePickerInput,
}

export default {
    name: "FormField",
    components: {
        ValidationErrors,
        RichTextInput,
    },
    props: {
        schema: Object,
        value: { required: true },
        vuelidate: Object,
    },
    computed: {
        widgetComponent() {
            return widgetComponentMap[this.schema.type]
        },
    },
    methods: {
        onInput(value) {
            if (this.vuelidate) {
                this.vuelidate.$touch()
            }
            this.$emit("input", value)
        },
    },
}
</script>
