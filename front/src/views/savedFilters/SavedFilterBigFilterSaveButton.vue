<template>
<button
    v-if="
        apiSource.hasFilter &&
        !(state == 'ready' && !tooltip) &&
        !loadingInProgress.fetchSavedFilters
    "
    class="button is-light rounded-l-none -ml-1"
    @click="onClick"
>
    <BarLoader v-if="state == 'loading'" />
    <template v-else-if="state == 'ready'">{{ tooltip }}</template>
    <template v-else-if="state == 'done'">{{ $t("saveDone") }}</template>
</button>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { parseQueryString } from "@js/queryString"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "SavedFilterBigFilterSaveButton",
    mixins: [PilotMixin],
    props: {
        apiSource: Object,
    },
    data: () => ({
        state: "ready",
    }),
    computed: {
        ...mapState("loading", ["loadingInProgress"]),
        ...mapGetters("savedFilter", [
            "isFilterTabOpen",
            "selectedSavedFilter",
            "isInternalSharedSavedFilter",
        ]),
        disabled() {
            // Special-case : always allow to save a shared filter
            if (this.isInternalSharedSavedFilter) {
                return false
            }

            // Don't compare the two query strings directly,
            // because the params may appear in different order.
            // Instead, parse them and compare the resulting objects.
            let currentParams = parseQueryString(this.apiSource.queryString),
                savedParams = parseQueryString(
                    this.selectedSavedFilter ? this.selectedSavedFilter.query : "",
                )
            // Remove the ordering and the start/end for calendar
            currentParams = _.omit(currentParams, ["order_by", "start", "end"])
            savedParams = _.omit(savedParams, ["order_by", "start", "end"])

            // Can't update the filter if the query string didn't change
            return (
                this.isFilterTabOpen &&
                this.selectedSavedFilter &&
                _.isEqual(currentParams, savedParams) &&
                this.state == "ready"
            )
        },
        tooltip() {
            if (this.disabled) {
                return null
            }
            if (this.isInternalSharedSavedFilter) return this.$t("saveSharedFilter")
            else if (this.isFilterTabOpen) return this.$t("updateFilterTooltip")
            else return this.$t("createFilterTooltip")
        },
    },
    methods: {
        ...mapActions("savedFilter", ["partialUpdateSavedFilter"]),
        onClick() {
            if (this.disabled || this.state != "ready") {
                return
            }

            // Shared filter copy
            if (this.isInternalSharedSavedFilter) {
                this.openOffPanel("savedFilterCreateUpdate")
            }
            // Filter update
            else if (this.isFilterTabOpen) {
                this.state = "loading"
                this.partialUpdateSavedFilter({
                    id: this.selectedSavedFilter.id,
                    query: this.apiSource.queryString,
                }).then(() => {
                    this.state = "done"
                    setTimeout(() => {
                        this.state = "ready"
                    }, 3000)
                })
            }
            // Filter creation
            else {
                this.openOffPanel("savedFilterCreateUpdate")
            }
        },
    },
    i18n: {
        messages: {
            fr: {
                createFilterTooltip: "Enregistrer",
                saveDone: "Ok, enregistré",
                saveSharedFilter: "Copier ce filtre partagé",
                updateFilterTooltip: "Le filtre a été modifié, enregistrer les changements ?",
            },
            en: {
                createFilterTooltip: "Save",
                saveDone: "Ok, saved",
                saveSharedFilter: "Copy this shared filter",
                updateFilterTooltip: "The filter has been modified, save the changes?",
            },
        },
    },
}
</script>
