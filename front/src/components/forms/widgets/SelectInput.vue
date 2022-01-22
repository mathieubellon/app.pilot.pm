<template>
<VueSelect
    :clearable="clearable"
    :multiple="multiple"
    :options="choices"
    :placeholder="actualPlaceholder"
    :reduce="reduce"
    :resetOnOptionsChange="resetOnOptionsChange"
    :value="actualValue"
    @input="$emit('input', $event)"
/>
</template>

<script>
/**
 * Expect choice in the format [{value: '', label: ''}, ...]
 *
 * Value can be of any type.
 *
 * When multiple == true, value will be an array of values
 *
 * /!\ WARNING : this component cannot be used inside a <label> element.
 * See https://github.com/sagalbot/vue-select/issues/505
 */
import _ from "lodash"
import VueSelect from "vue-select"

export default {
    name: "SelectInput",
    components: {
        VueSelect,
    },
    props: {
        value: {},
        choices: {},
        multiple: {},
        placeholder: {},
        clearable: {
            type: Boolean,
            default: true,
        },
        resetOnOptionsChange: {},
        reduce: {
            type: Function,
            default: (option) => option.value,
        },
    },
    computed: {
        actualValue() {
            if (this.multiple) {
                if (!this.value) {
                    return []
                }
                return _.filter(this.choices, (choice) => this.value.includes(choice.value))
            } else {
                return _.find(this.choices, (choice) => choice.value == this.value)
            }
        },
        actualPlaceholder() {
            if (this.clearable && !this.placeholder) return this.$t("vueSelectPlaceholder")
            return this.placeholder
        },
    },
}
</script>
