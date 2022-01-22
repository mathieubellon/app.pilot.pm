<template>
<VueSelect
    :clearable="false"
    :options="iconChoices"
    :value="iconValue"
    @input="$emit('input', $event ? $event.value : null)"
>
    <template v-slot:selected-option="option">
        <component :is="option.iconComponent" />
        &nbsp;{{ option.label }}
    </template>

    <template v-slot:option="option">
        <component :is="option.iconComponent" />
        &nbsp;{{ option.label }}
    </template>
</VueSelect>
</template>

<script>
import _ from "lodash"
import VueSelect from "vue-select"
import { ITEM_TYPE_ICONS } from "./ItemTypeIcon"

export default {
    name: "ItemTypeIconSelect",
    components: {
        VueSelect,
    },
    props: {
        value: {},
    },
    computed: {
        iconValue() {
            return _.find(this.iconChoices, (choice) => choice.value == this.value)
        },
        iconChoices() {
            return _.map(ITEM_TYPE_ICONS, (icon, iconName) => {
                return {
                    value: iconName,
                    label: iconName,
                    iconComponent: icon,
                }
            })
        },
    },
}
</script>
