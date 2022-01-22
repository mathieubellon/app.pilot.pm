<template>
<img
    class="UserAvatar"
    :style="style"
    :src="user.avatar"
/>
</template>

<script>
export default {
    name: "UserAvatar",
    props: {
        user: Object,
        size: {
            type: String,
            default: "36px",
        },
    },
    computed: {
        style() {
            return {
                width: this.size,
                height: this.size,
                "border-radius": "5px",
            }
        },
    },
}
</script>
