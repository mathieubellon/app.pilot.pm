<template>
<input
    :checked="value"
    type="checkbox"
    @change="$emit('input', $event.target.checked)"
/>
</template>

<script>
export default {
    name: "CheckboxInput",
    props: ["schema", "value"],
}
</script>
