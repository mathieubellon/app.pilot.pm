<template>
<button
    class="button"
    :class="computedClasses"
    :style="computedStyle"
    :disabled="disabled"
    @click="$emit('click', $event)"
>
    <transition
        name="slide-fade"
        mode="out-in"
    >
        <BarLoader
            v-if="isLoading"
            color="#FFF"
            :loading="isLoading"
            :width="80"
            widthUnit="%"
        />
        <span v-else-if="status == 'success'">{{ successText }}</span>
        <span v-else-if="status == 'error'">{{ errorText }}</span>
    </transition>

    <slot v-if="!isLoading && !status"></slot>
</button>
</template>

<script>
import $ from "jquery"
import { BarLoader } from "@saeris/vue-spinners"
import i18n from "@js/i18n"

export default {
    name: "ButtonSpinner",
    components: {
        BarLoader,
    },
    props: {
        isLoading: {
            type: Boolean,
            default: false,
        },
        disabled: {
            type: Boolean,
            default: false,
        },
        status: {
            type: String,
            default: null,
        },
        successText: {
            type: String,
            default: i18n.t("ok"),
        },
        errorText: {
            type: String,
            default: i18n.t("error"),
        },
    },
    data: () => ({
        buttonHeight: null,
        buttonWidth: null,
    }),
    computed: {
        computedClasses() {
            return {
                //disabled: this.disabled,
                "is-red": this.status == "error",
                "is-green": this.status == "success",
                disabled: this.disabled,
            }
        },
        computedStyle() {
            return this.buttonWidth
                ? { "min-width": this.buttonWidth + "px", "min-height": this.buttonHeight + "px" }
                : {}
        },
    },
    watch: {
        isLoading() {
            if (this.isLoading) {
                this.buttonHeight = $(this.$el).outerHeight()
                this.buttonWidth = $(this.$el).outerWidth()
            }
        },
    },
}
</script>
