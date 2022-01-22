<template>
<App>
    <transition
        slot="main"
        enter-active-class="animated animated-150 fadeIn"
        leave-active-class="animated animated-150 fadeOut"
        mode="out-in"
    >
        <router-view />
    </transition>
</App>
</template>

<script>
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"
import App from "@components/layout/App.vue"

export default {
    name: "MainApp",
    components: {
        App,
    },
    data: () => ({
        lastProjectFetch: null,
        lastItemFetch: null,
    }),
    computed: {
        ...mapGetters("savedFilter", ["selectedSavedFilter"]),
    },
    methods: {
        ...mapMutations("sharings", ["setSharings"]),
        ...mapMutations("savedFilter", ["setLastSelectedSavedFilter"]),
    },
    watch: {
        selectedSavedFilter(newVal, oldVal) {
            if (newVal && oldVal && newVal.id == oldVal.id) {
                return
            }

            if (this.selectedSavedFilter) {
                this.setLastSelectedSavedFilter(this.selectedSavedFilter)
                this.setSharings(this.selectedSavedFilter.sharings)
            }
        },
    },
}
</script>
