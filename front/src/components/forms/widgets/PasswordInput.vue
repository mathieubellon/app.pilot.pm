<template>
<input
    class="PasswordInput"
    :placeholder="schema.placeholder"
    type="password"
    :value="value"
    @input="$emit('input', $event.target.value)"
/>
</template>

<script>
export default {
    name: "PasswordInput",
    props: ["schema", "value"],
}
</script>
