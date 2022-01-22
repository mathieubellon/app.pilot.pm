<template>
<div
    class="Picker__Element"
    :class="{ picked, disabled }"
    :disbaled="disabled"
    @click="onClick"
>
    <div class="Picker__Element__Name">
        <input
            :checked="picked"
            type="checkbox"
        />
        <div>{{ target.name }}</div>
    </div>
</div>
</template>

<script>
export default {
    name: "TargetPickerElement",
    props: {
        target: Object,
        picked: Boolean,
        disabled: Boolean,
    },
    methods: {
        onClick() {
            if (!this.disabled) this.$emit("pick", this.target)
        },
    },
}
</script>
