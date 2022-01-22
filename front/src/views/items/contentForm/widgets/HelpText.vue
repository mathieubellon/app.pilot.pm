<template>
<div class="ItemContentHelpText">
    <span
        v-if="helpText"
        v-html="helpText"
    />
</div>
</template>

<script>
import { translateItemFieldAttribute } from "@js/localize.js"

export default {
    name: "HelpText",
    props: ["schema", "value"],
    computed: {
        helpText() {
            return translateItemFieldAttribute(this.schema.help_text)
        },
    },
}
</script>
