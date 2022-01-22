<template>
<div class="ItemCalendar">
    <div
        v-if="isInternalSharedSavedFilter"
        class="alert-panel is-yellow"
    >
        {{ $t("internalSharedFilterMessage", { creator: selectedSavedFilter.user.username }) }}
    </div>

    <BigFilter
        :apiSource="itemsApiSource"
        :canSave="true"
        filterSchemaUrl="/api/big_filter/schema/items/calendar/"
    />

    <FullCalendar v-if="calendarReady" />

    <SavedFilterCreateUpdatePanel
        :filtersQueryString="itemsApiSource.queryString"
        :isCalendar="true"
    />

    <SavedFilterInternalSharePanel />

    <SavedFilterDeletePanel goToAfterDelete="calendar-main" />

    <SharingsModal
        :sharingTarget="{
            type: 'calendar',
            saved_filter_id: savedFilterId,
        }"
    />
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import FullCalendar from "./FullCalendar.vue"
import BigFilter from "@views/bigFilter/BigFilter.vue"

import SavedFilterCreateUpdatePanel from "@views/savedFilters/SavedFilterCreateUpdatePanel.vue"
import SavedFilterInternalSharePanel from "@views/savedFilters/SavedFilterInternalSharePanel.vue"
import SavedFilterBigFilterSaveButton from "@views/savedFilters/SavedFilterBigFilterSaveButton.vue"
import SavedFilterDeletePanel from "@views/savedFilters/SavedFilterDeletePanel.vue"
import SharingsModal from "@views/sharings/internal/SharingsModal"

export default {
    name: "ItemCalendar",
    mixins: [PilotMixin],
    components: {
        BigFilter,
        FullCalendar,

        SavedFilterCreateUpdatePanel,
        SavedFilterInternalSharePanel,
        SavedFilterBigFilterSaveButton,
        SavedFilterDeletePanel,
        SharingsModal,
    },
    data: () => ({
        calendarReady: false,
    }),
    computed: {
        ...mapState("calendar", ["itemsApiSource"]),
        ...mapGetters("savedFilter", [
            "savedFilterId",
            "selectedSavedFilter",
            "isInternalSharedSavedFilter",
            "isFilterTabOpen",
        ]),
    },
    methods: {
        ...mapActions("calendar", ["fetchCalendarEvents"]),
        ...mapActions("savedFilter", ["fetchSavedFilters"]),
    },
    created() {
        // If we're loading a filter view,
        // we must wait for the filter query before loading the items
        if (this.isFilterTabOpen) {
            this.fetchSavedFilters().then(() => {
                // With sliding calendars, the FullCalendar watcher on 'itemsApiSource.url' will fetch the events
                // after setting the dates
                if (!this.selectedSavedFilter.is_sliding_calendar) {
                    this.fetchCalendarEvents()
                }
                this.calendarReady = true
            })
        } else {
            this.fetchCalendarEvents()
            this.calendarReady = true
        }
    },
    i18n: {
        messages: {
            fr: {
                internalSharedFilterMessage:
                    "Ce filtre a été partagé par {creator}. Vous pouvez le copier dans vos filtres personnels.",
            },
            en: {
                internalSharedFilterMessage:
                    "This filter has been shared by {creator}. You can copy it into your personnal filters.",
            },
        },
    },
}
</script>
