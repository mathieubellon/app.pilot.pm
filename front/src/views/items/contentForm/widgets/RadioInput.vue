<template>
<div class="p-2 rounded-sm border border-gray-200 bg-gray-100">
    <div v-for="choice in choices">
        <label class="my-3 cursor-pointer hover:cursor-pointer flex items-center">
            <input
                :checked="value == choice.value"
                :name="schema.name"
                type="radio"
                :value="choice.value"
                @change="$emit('input', $event.target.value)"
            />
            <span class="ml-2 leading-none">{{ choice.label }}</span>
        </label>
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { translateItemFieldAttribute } from "@js/localize.js"

export default {
    name: "RadioInput",
    props: ["schema", "value"],
    computed: {
        choices() {
            return this.schema.choices.map((choice) => ({
                value: choice[0],
                label: translateItemFieldAttribute(choice[1]),
            }))
        },
    },
}
</script>
<style lang="scss">
@import "~@sass/common_variables.scss";
.RadioInput {
    @apply p-2 rounded-sm;
    font-size: $field-font-size;
    background-color: $field-background-color;
    color: $field-color;
    border: $field-border;
    border-radius: $field-border-radius;
    caret-color: $field-caret-color;
}
</style>
