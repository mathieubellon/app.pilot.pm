<template>
<ToggleButton
    :labels="labels"
    :sync="true"
    :value="value"
    @input="$emit('input', !value)"
/>
</template>

<script>
import { ToggleButton } from "vue-js-toggle-button"

export default {
    name: "ToggleInput",
    components: {
        ToggleButton,
    },
    props: ["schema", "value"],
    computed: {
        labels() {
            let i18n = {
                en: { checked: "on", unchecked: "off" },
                fr: { checked: "oui", unchecked: "non" },
            }
            return i18n[window.pilot.currentLocale]
        },
    },
}
</script>
