<template>
<Fragment>
    <slot
        v-if="nameInLoading"
        name="loader"
    >
        <span class="Loadarium__center text-xs text-blue-900 px-1">
            <Loading :name="nameInLoading" />
        </span>
    </slot>
    <span
        v-else-if="nameInError"
        class="Loadarium__center"
    >
        <LoadingError
            :label="errorLabel"
            :name="nameInError"
        />
    </span>
    <slot v-else />
</Fragment>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"

import { Fragment } from "vue-fragment"
import Loading from "./Loading"
import LoadingError from "./LoadingError"

export default {
    name: "Loadarium",
    components: {
        Fragment,
        Loading,
        LoadingError,
    },
    props: {
        name: {
            type: [Array, String],
            required: true,
        },
        errorLabel: String,
    },
    computed: {
        ...mapState("loading", ["loadingInProgress", "loadingErrors"]),
        names() {
            if (_.isArray(this.name)) {
                return this.name
            }
            return [this.name]
        },
        nameInLoading() {
            for (let name of this.names) {
                if (this.loadingInProgress[name]) {
                    return name
                }
            }
            return false
        },
        nameInError() {
            for (let name of this.names) {
                if (this.loadingErrors[name]) {
                    return name
                }
            }
            return null
        },
    },
}
</script>

<style lang="scss">
.Loadarium__center {
    width: auto;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
</style>
