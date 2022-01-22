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
        <div>
            <UserAvatar
                class="UserPickerElement__avatar"
                size="20px"
                :user="user"
            />
        </div>
        <div>@{{ user.username }}</div>
    </div>
</div>
</template>

<script>
import PilotMixin from "@components/PilotMixin"

export default {
    name: "UserPickerElement",
    mixins: [PilotMixin],
    props: {
        user: Object,
        picked: Boolean,
        disabled: Boolean,
    },
    methods: {
        onClick() {
            if (!this.disabled) this.$emit("pick", this.user)
        },
    },
}
</script>
