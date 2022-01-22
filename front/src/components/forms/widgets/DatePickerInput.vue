<template>
<DatePicker
    :enableTime="schema.enableTime"
    :formatWithoutTime="schema.formatWithoutTime"
    :hideInput="schema.hideInput"
    :inline="schema.inline"
    :naiveTime="schema.naiveTime"
    v-on="listeners"
    :value="value"
    @input="$emit('input', $event)"
/>
</template>

<script>
import DatePicker from "@components/forms/widgets/DatePicker"

export default {
    name: "DatePickerInput",
    components: {
        DatePicker,
    },
    props: ["schema", "value"],
    computed: {
        // See https://zendev.com/2018/05/31/transparent-wrapper-components-in-vue.html
        listeners() {
            const { input, ...listeners } = this.$listeners
            return listeners
        },
    },
}
</script>
