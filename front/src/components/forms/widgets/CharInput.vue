<template>
<input
    :placeholder="placeholder"
    type="text"
    :value="value"
    @input="$emit('input', $event.target.value)"
/>
</template>

<script>
import { translateItemFieldAttribute } from "@js/localize"

export default {
    name: "CharInput",
    props: ["schema", "value"],
    computed: {
        placeholder() {
            return translateItemFieldAttribute(this.schema.placeholder)
        },
    },
}
</script>
