<template>
<textarea
    ref="textarea"
    :readonly="readOnly"
    v-bind="placeholderAttr"
    v-on="listeners"
    :value="value"
    @input="updateValue"
/>
</template>

<script>
import $ from "jquery"
import autosize from "autosize"

export default {
    name: "TextAreaAutosize",
    props: {
        value: String,
        placeholder: {
            type: String,
            default: "",
        },
        readOnly: {
            type: Boolean,
            default: false,
        },
    },
    computed: {
        textarea() {
            return this.$refs.textarea
        },
        // See https://zendev.com/2018/05/31/transparent-wrapper-components-in-vue.html
        listeners() {
            const { input, ...listeners } = this.$listeners
            return listeners
        },
        /**
         * !! Please Read Carefully. !!
         * We need this crappy v-bind="placeholderAttr" construct because of crappy IE.
         * It won't handle correctly the input event if we pass it an empty string as placeholder.
         * Other browsers are fine, of course.
         */
        placeholderAttr() {
            if (this.placeholder) {
                return { placeholder: this.placeholder }
            }
            return {}
        },
    },
    watch: {
        value() {
            this.triggerAutosize()
        },
    },
    methods: {
        updateValue($event) {
            this.$emit("input", $event.target.value)
        },
        /**
         * autosize API is a bit lame, we cannot know if it has already been initialized.
         * But there's no side effect on calling init multiple time.
         * So we just call the init each time ( useful only for the first call ),
         * and update each time ( useful for the subsequent calls )
         */
        triggerAutosize() {
            this.$nextTick(() => {
                autosize(this.textarea)
                autosize.update(this.textarea)
            })
        },
    },
    mounted() {
        // If there's already a value available, autosize right now
        if (this.value) {
            this.triggerAutosize()
        }
        // Else wait for the textarea to gain focus to activate autosize.
        // This will prevent textarea that are displayed with an animation
        // to end up with an incorrect height.
        else {
            $(this.textarea).on("focus", () => this.triggerAutosize())
        }
    },
    beforeDestroy() {
        $(this.textarea).off("focus")
        autosize.destroy(this.textarea)
    },
}
</script>
