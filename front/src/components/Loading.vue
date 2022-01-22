<template>
<span v-if="loadingInProgress[name]">
    <slot>
        <BarLoader
            class="my-1"
            color="#3182CE"
            :loading="true"
            :width="200"
            widthUnit="px"
        />
    </slot>
</span>
</template>

<script>
import { mapState } from "vuex"

import { BarLoader } from "@saeris/vue-spinners"

export default {
    name: "Loading",
    components: {
        BarLoader,
    },
    props: {
        name: {
            type: String,
            required: true,
        },
        size: String,
    },
    computed: {
        ...mapState("loading", ["loadingInProgress"]),
    },
}
</script>
