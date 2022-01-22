<template>
<div
    v-if="error"
    class="LoadingError"
>
    <div>{{ label }}</div>
    <div>{{ error }}</div>
</div>
</template>

<script>
import { mapGetters } from "vuex"
import i18n from "@js/i18n"

export default {
    name: "LoadingError",
    props: {
        name: {
            type: String,
            required: true,
        },
        label: {
            type: String,
            default: i18n.t("loadingError"),
        },
    },
    computed: {
        ...mapGetters("loading", ["getErrorMessage"]),
        error() {
            return this.getErrorMessage(this.name)
        },
    },
}
</script>
