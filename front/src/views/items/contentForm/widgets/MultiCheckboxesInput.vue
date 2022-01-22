<template>
<div class="MultiCheckBoxInput">
    <div v-for="choice in choices">
        <label class="my-3 cursor-pointer hover:cursor-pointer flex items-center">
            <input
                v-model="selection[choice.value]"
                type="checkbox"
                @change="updateValue"
            />
            <span class="ml-2 leading-none">{{ choice.label }}</span>
        </label>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import { translateItemFieldAttribute } from "@js/localize.js"

export default {
    name: "MultiCheckboxesInput",
    props: ["schema", "value"],
    data: () => ({
        selection: {},
    }),
    computed: {
        choices() {
            return this.schema.choices.map((choice) => ({
                value: choice[0],
                label: translateItemFieldAttribute(choice[1]),
            }))
        },
    },
    watch: {
        value() {
            this.updateSelection()
        },
    },
    methods: {
        updateValue() {
            let newValue = _.keys(_.pickBy(this.selection, (value) => value == true)).map((key) =>
                parseInt(key),
            )
            this.$emit("input", newValue)
        },
        updateSelection() {
            if (!this.value) {
                return
            }
            this.selection = {}
            for (let choiceName of this.value) {
                this.selection[choiceName] = true
            }
        },
    },
    created() {
        this.updateSelection()
    },
}
</script>

<style lang="scss">
@import "~@sass/common_variables.scss";
.MultiCheckBoxInput {
    @apply p-2 rounded-sm;
    font-size: $field-font-size;
    background-color: $field-background-color;
    color: $field-color;
    border: $field-border;
    border-radius: $field-border-radius;
    caret-color: $field-caret-color;
}
</style>
