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
        <div>{{ project.name }}</div>
    </div>
</div>
</template>

<script>
export default {
    name: "ProjectPickerElement",
    props: {
        project: Object,
        picked: Boolean,
        disabled: Boolean,
    },
    methods: {
        onClick() {
            if (!this.disabled) this.$emit("pick", this.project)
        },
    },
}
</script>
