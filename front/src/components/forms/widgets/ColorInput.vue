<template>
<ColorPickerCurated
    :value="colorValue"
    @input="onInput"
/>
</template>

<script>
import ColorPickerCurated from "@components/ColorPickerCurated"

export default {
    name: "ColorInput",
    components: {
        ColorPickerCurated,
    },
    props: ["schema", "value"],
    computed: {
        colorValue() {
            if (this.schema.inputType == "background") {
                return { backgroundColor: this.value }
            } else {
                return this.value
            }
        },
    },
    methods: {
        onInput($event) {
            if (this.schema.inputType == "background") {
                this.$emit("input", $event.backgroundColor)
            } else {
                this.$emit("input", $event)
            }
        },
    },
}
</script>
