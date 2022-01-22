<template>
<MainLayout>
    <template slot="title">{{ $t("contents") }}</template>

    <ItemListTabs slot="middlebar" />

    <template #actions>
        <ItemListTopBarActions />
    </template>

    <template #content>
        <router-view class="p-2 md:p-8 md:pr-4" />
    </template>
</MainLayout>
</template>

<script>
import _ from "lodash"
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"
import { getItemApiSource } from "@js/apiSource"
import PilotMixin from "@components/PilotMixin"

import MainLayout from "@components/layout/MainLayout"
import ItemListTabs from "./ItemListTabs"
import ItemListTopBarActions from "./ItemListTopBarActions"

export default {
    name: "ItemListApp",
    mixins: [PilotMixin],
    components: {
        MainLayout,
        ItemListTabs,
        ItemListTopBarActions,
    },
    data: () => ({
        lastFetchRouteName: null,
    }),
    computed: {
        ...mapState("itemList", ["apiSource", "savedQueries"]),
        ...mapGetters("savedFilter", ["selectedSavedFilter"]),
    },
    methods: {
        ...mapMutations("itemList", ["setApiSource", "saveQuery"]),
        ...mapActions("savedFilter", ["fetchSavedFilters"]),
        applySavedQuery() {
            // The query string in the url has priority over the savedQuery
            // Don't apply the savedQuery if there's already a query string in the url.
            if (!document.location.search) {
                this.apiSource.setQuery(this.savedQueries[this.currentRouteName])
            }
        },
    },
    watch: {
        "apiSource.url"() {
            // Apply the saved query string when the route changes
            if (this.currentRouteName != this.lastFetchRouteName) {
                this.applySavedQuery()
            }

            this.lastFetchRouteName = this.currentRouteName

            // The only case where apiSource query may be empty is when we land on a new page.
            // In this case we don't want to erase the saved query with our empty query.
            if (!_.isEmpty(this.apiSource.query)) {
                this.saveQuery({
                    routeName: this.currentRouteName,
                    query: this.apiSource.query,
                })
            }
        },

        selectedSavedFilter(newVal, oldVal) {
            if (newVal && oldVal && newVal.id == oldVal.id) {
                return
            }

            // Use the savedFilter to populate the BigFilter
            if (this.selectedSavedFilter) {
                this.apiSource.setQueryString(this.selectedSavedFilter.query)
            }
        },
    },
    created() {
        this.fetchSavedFilters()
        this.setApiSource(getItemApiSource())
        this.applySavedQuery()
    },
}
</script>
