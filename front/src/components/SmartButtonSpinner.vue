<template>
<ButtonSpinner
    :disabled="loadingInProgress[name] || status == 'success'"
    :errorText="getErrorMessage(name)"
    :isLoading="loadingInProgress[name]"
    :status="status"
    :successText="successText"
    @click="$emit('click', $event)"
>
    <slot></slot>
</ButtonSpinner>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"

import ButtonSpinner from "@components/ButtonSpinner.vue"

export default {
    name: "SmartButtonSpinner",
    components: {
        ButtonSpinner,
    },
    props: {
        name: String,
        successText: String,
        timeout: Number,
    },
    computed: {
        ...mapState("loading", ["loadingInProgress", "loadingStatus", "loadingErrors"]),
        ...mapGetters("loading", ["getErrorMessage"]),
        status() {
            return this.loadingStatus[this.name]
        },
    },
    watch: {
        // When the status change, if a timeout is defined, reset to the initial state
        status() {
            if (_.isNumber(this.timeout) && this.status) {
                setTimeout(() => {
                    this.resetLoading(this.name)
                    this.$emit("reset")
                }, this.timeout)
            }
        },
    },
    methods: {
        ...mapMutations("loading", ["resetLoading"]),
    },
    created() {
        this.resetLoading(this.name)
    },
}
</script>
