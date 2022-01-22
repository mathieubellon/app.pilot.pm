<template>
<TextAreaAutosize
    class="CharInputWrapping"
    ref="TextAreaAutosize"
    :placeholder="schema ? schema.placeholder : ''"
    rows="1"
    v-on="listeners"
    :value="value"
    @input="updateValue"
    @keydown.enter.prevent="onEnter"
/>
</template>

<script>
import TextAreaAutosize from "./TextAreaAutosize"

export default {
    name: "CharInputWrapping",
    components: {
        TextAreaAutosize,
    },
    props: ["schema", "value"],
    computed: {
        // See https://zendev.com/2018/05/31/transparent-wrapper-components-in-vue.html
        listeners() {
            const { input, ...listeners } = this.$listeners
            return listeners
        },
    },
    methods: {
        updateValue(value) {
            // Prevent carriage return
            this.$emit("input", value.replace(/\n/g, ""))
        },
        onEnter() {
            this.$el.dispatchEvent(
                new CustomEvent("CharInputWrappingSubmit", {
                    detail: null,
                    bubbles: true,
                    composed: true,
                }),
            )
        },
    },
    mounted() {
        this.$refs.TextAreaAutosize.triggerAutosize()
    },
}
</script>

<style lang="scss">
@import "~@sass/common_variables.scss";

.CharInputWrapping {
    min-height: $field-min-height;
    @apply p-3;
}
</style>
