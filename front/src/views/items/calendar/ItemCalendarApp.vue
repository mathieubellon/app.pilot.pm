<template>
<MainLayout>
    <template #title>
        {{ $t("calendars") }}
    </template>

    <template #actions>
        <ItemCalendarTopBarActions />
    </template>

    <template #middlebar>
        <ItemCalendarTabs />
    </template>

    <template #content>
        <div class="p-2 md:p-8 md:pr-4">
            <router-view :key="currentRouteName" />
        </div>
    </template>
</MainLayout>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { getItemCalendarApiSource, getProjectCalendarApiSource } from "@js/apiSource"
import { QueryParamSerializer } from "@js/queryString"

import PilotMixin from "@components/PilotMixin"
import MainLayout from "@components/layout/MainLayout"
import ItemCalendarTabs from "./ItemCalendarTabs"
import ItemCalendarTopBarActions from "./ItemCalendarTopBarActions"

export default {
    name: "ItemCalendarApp",
    mixins: [PilotMixin],
    components: {
        MainLayout,
        ItemCalendarTabs,
        ItemCalendarTopBarActions,
    },
    data: () => ({
        lastFetchRouteName: null,
    }),
    computed: {
        ...mapState("calendar", ["itemsApiSource", "savedQueries"]),
        ...mapGetters("savedFilter", ["selectedSavedFilter"]),
    },
    methods: {
        ...mapMutations("calendar", ["setItemsApiSource", "setProjectsApiSource", "saveQuery"]),
        ...mapActions("savedFilter", ["fetchSavedFilters"]),
        applySavedQuery() {
            // The query string in the url has priority over the savedQuery
            // Don't apply the savedQuery if there's already a query string in the url.
            if (!document.location.search) {
                this.itemsApiSource.setQuery(this.savedQueries[this.currentRouteName])
            }
        },
    },
    watch: {
        "itemsApiSource.url"() {
            // Apply the saved query string when the route changes
            if (this.currentRouteName != this.lastFetchRouteName) {
                this.applySavedQuery()
            }

            this.lastFetchRouteName = this.currentRouteName

            // The only case where apiSource query may be empty is when we land on a new page.
            // In this case we don't want to erase the saved query with our empty query.
            if (!_.isEmpty(this.itemsApiSource.query)) {
                this.saveQuery({
                    routeName: this.currentRouteName,
                    query: this.itemsApiSource.query,
                })
            }
        },

        selectedSavedFilter(newVal, oldVal) {
            if (newVal && oldVal && newVal.id == oldVal.id) {
                return
            }

            if (this.selectedSavedFilter) {
                let serializer = new QueryParamSerializer(this.selectedSavedFilter.query)
                if (this.selectedSavedFilter.is_sliding_calendar) {
                    serializer.removeParam("start")
                    serializer.removeParam("end")
                }
                this.itemsApiSource.setQuery(serializer.params)
            }
        },
    },
    created() {
        this.fetchSavedFilters()
        this.setItemsApiSource(getItemCalendarApiSource())
        this.setProjectsApiSource(getProjectCalendarApiSource())
        this.applySavedQuery()
    },
    i18n: {
        messages: {
            fr: {
                calendars: "Calendriers des tâches et projets",
            },
            en: {
                calendars: "Tasks and projects calendars",
            },
        },
    },
}
</script>
