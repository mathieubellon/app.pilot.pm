<template>
<VueSelect
    :options="options"
    :taggable="true"
    :value="value"
    @input="$emit('input', $event)"
/>
</template>

<script>
import VueSelect from "vue-select"

export default {
    name: "AutoCompleteInput",
    components: {
        VueSelect,
    },
    props: ["schema", "value"],
    computed: {
        options() {
            return this.schema.choices.map((choice) => choice[1])
        },
    },
}
</script>
