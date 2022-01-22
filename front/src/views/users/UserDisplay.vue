<template>
<Fragment>
    <span v-if="!user">?</span>
    <span
        v-else-if="isExternal"
        :class="computedClass"
        :style="style"
    >
        {{ user.username }}
    </span>
    <span
        v-else-if="withAvatar && withUsername"
        class="inline-flex"
        :class="computedClass"
        :style="style"
        @click="openUserDetails()"
    >
        <UserAvatar
            class="rounded-full mr-1"
            :size="avatarSize"
            :user="user"
        />
        <span>@{{ user.username }}</span>
    </span>
    <UserAvatar
        v-else-if="withAvatar && !withUsername"
        class="inline-flex rounded-full"
        :class="computedClass"
        :size="avatarSize"
        :user="user"
        @click="openUserDetails()"
    />
    <span
        v-else
        class="inline-flex"
        :class="computedClass"
        @click="openUserDetails()"
    >
        @{{ user.username }}
    </span>
</Fragment>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"

import { Fragment } from "vue-fragment"
import UserAvatar from "./UserAvatar"

export default {
    name: "UserDisplay",
    components: {
        Fragment,
        UserAvatar,
    },
    props: {
        user: {
            required: true,
        },
        withAvatar: {
            type: Boolean,
            default: false,
        },
        withUsername: {
            type: Boolean,
            default: true,
        },
        avatarSize: {
            type: String,
            default: "20px",
        },
        color: String,
        aClass: {
            default: "",
        },
    },
    computed: {
        isExternal() {
            return !_.isInteger(this.user.id)
        },
        style() {
            if (this.color) return { color: this.color }
            return {}
        },
        computedClass() {
            if (this.user.wiped) {
                return ""
            } else {
                return "UserDisplay " + this.aClass
            }
        },
    },
    methods: {
        ...mapMutations("offPanel", ["openOffPanel"]),
        ...mapActions("users", ["fetchUserExamined"]),
        openUserDetails() {
            if (this.user.wiped) {
                return
            }
            this.fetchUserExamined(this.user.id)
            this.openOffPanel("UserExaminationPanel")
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.UserDisplay {
    @apply cursor-pointer;

    &:hover {
        @apply bg-indigo-100;
    }
}
</style>
