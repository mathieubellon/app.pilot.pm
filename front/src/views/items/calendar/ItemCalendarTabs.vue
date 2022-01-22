<template>
<div class="tabs">
    <router-link
        class="tab"
        active-class="is-active"
        :to="{ name: 'calendar-main' }"
    >
        {{ $t("mainCalendar") }}
    </router-link>
    <router-link
        v-if="lastSelectedSavedFilter && lastSelectedSavedFilter.type == 'calendar'"
        class="tab"
        active-class="is-active"
        :to="{ name: 'calendar-filter', params: { id: lastSelectedSavedFilter.id } }"
    >
        {{ lastSelectedSavedFilter.title }}
    </router-link>

    <SavedFiltersPopper type="calendar" />
</div>
</template>

<script>
import { mapState, mapMutations, mapActions } from "vuex"
import PilotMixin from "@components/PilotMixin"
import SavedFiltersPopper from "@views/savedFilters/SavedFiltersPopper"

export default {
    name: "ItemCalendarTabs",
    mixins: [PilotMixin],
    components: {
        SavedFiltersPopper,
    },
    computed: {
        ...mapState("savedFilter", ["lastSelectedSavedFilter"]),
    },
    i18n: {
        messages: {
            fr: {
                mainCalendar: "Calendrier principal",
            },
            en: {
                mainCalendar: "Main calendar",
            },
        },
    },
}
</script>
