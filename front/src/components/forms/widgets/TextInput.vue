<template>
<TextAreaAutosize
    :placeholder="placeholder"
    :value="value"
    @input="$emit('input', $event)"
/>
</template>

<script>
import TextAreaAutosize from "./TextAreaAutosize"
import { translateItemFieldAttribute } from "@js/localize"

export default {
    name: "TextInput",
    components: { TextAreaAutosize },
    props: ["schema", "value"],
    computed: {
        placeholder() {
            return translateItemFieldAttribute(this.schema.placeholder)
        },
    },
}
</script>
