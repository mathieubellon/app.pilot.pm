<template>
<SelectInput
    :choices="choices"
    :clearable="!schema.required"
    :multiple="schema.multiple"
    :placeholder="placeholder"
    :value="value"
    @input="updateValue"
/>
</template>

<script>
import _ from "lodash"
import SelectInput from "./SelectInput.vue"
import { translateItemFieldAttribute } from "@js/localize"

export default {
    name: "ChoiceInput",
    components: { SelectInput },
    props: ["schema", "value"],
    computed: {
        choices() {
            // Empty choices
            if (!this.schema.choices || _.isEmpty(this.schema.choices)) {
                return []
            }
            // Choices already have the correct format
            if (this.schema.choices[0].value && this.schema.choices[0].label) {
                return this.schema.choices
            }
            // Choices are an array of pairs
            return this.schema.choices.map((choice) => ({
                value: choice[0],
                label: translateItemFieldAttribute(choice[1]),
            }))
        },
        placeholder() {
            return translateItemFieldAttribute(this.schema.placeholder)
        },
    },
    methods: {
        updateValue(value) {
            this.$emit("input", value)
        },
    },
}
</script>
