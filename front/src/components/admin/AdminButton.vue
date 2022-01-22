<template>
<a
    :class="computedClass"
    :disabled="isDisabled"
    v-tooltip="isDisabled ? $t('adminOnly') : null"
    @click="onCLick"
>
    <slot />
</a>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"

export default {
    name: "AdminButton",
    props: {
        aClass: {
            default: "button is-blue",
        },
        checkPerm: {
            type: Boolean,
            default: true,
        },
    },
    computed: {
        ...mapGetters("users", ["myPermissions"]),
        computedClass() {
            let computedClass = this.aClass
            if (this.isDisabled) {
                computedClass += " disabled"
            }
            return computedClass
        },
        isDisabled() {
            return this.checkPerm && !this.myPermissions.is_admin
        },
    },
    methods: {
        onCLick(event) {
            if (this.isDisabled) {
                event.preventDefault()
                event.stopImmediatePropagation()
            } else {
                this.$emit("click")
            }
        },
    },
    i18n: {
        messages: {
            fr: {
                adminOnly: "Uniquement autorisé aux administateurs/trices",
            },
            en: {
                adminOnly: "Only allowed to administrators",
            },
        },
    },
}
</script>
