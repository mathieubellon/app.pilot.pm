<template>
<Popper
    ref="SavedFiltersPopper"
    triggerElementName="PopperRef"
>
    <template #triggerElement>
        <a
            class="tab"
            ref="PopperRef"
        >
            {{ $t("savedFilters") }}
            <!-- The empty span is required to correctly align with flex display -->
            <span>
                <Icon
                    class="caret"
                    name="ChevronDown"
                />
            </span>
        </a>
    </template>

    <template #content>
        <Loadarium name="fetchSavedFilters">
            <div slot="loader">
                {{ $t("loading") }}
            </div>

            <div
                v-if="sortedSavedFilter.length > 0"
                class="h-64 max-w-md overflow-y-auto overflow-x-hidden"
            >
                <div class="font-black text-sm px-4">
                    {{ $t("mySavedFilters") }}
                </div>
                <a
                    v-for="savedFilter in sortedSavedFilter"
                    class="menu-item mr-4"
                    @click="selectSavedFilter(savedFilter)"
                >
                    {{ savedFilter.title }}
                </a>
            </div>
            <div
                v-else
                class="w-64 leading-tight"
            >
                <div class="font-semibold">{{ $t("noFilter") }}</div>
                <div class="text-gray-700">{{ $t("howToAddFilters") }}</div>
            </div>
        </Loadarium>
    </template>
</Popper>
</template>

<script>
import _ from "lodash"
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import { sortByAlphaString } from "@js/utils.js"
import { parseQueryString } from "@js/queryString"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "SavedFiltersPopper",
    mixins: [PilotMixin],
    props: {
        type: String,
    },
    computed: {
        ...mapState("users", ["me"]),
        ...mapState("savedFilter", ["savedFilters"]),
        sortedSavedFilter() {
            return sortByAlphaString(
                this.savedFilters.filter(
                    (savedFilter) =>
                        savedFilter.type == this.type && savedFilter.user.id == this.me.id,
                ),
                (savedFilter) => savedFilter.title,
            )
        },
    },
    methods: {
        selectSavedFilter(savedFilter) {
            // Navigate to the filter tab
            let routeName = this.type == "list" ? "itemList-filter" : "calendar-filter"
            this.$router.push({
                name: routeName,
                params: { id: savedFilter.id },
                query: parseQueryString(savedFilter.query),
            })
            this.$refs.SavedFiltersPopper.hidePopper()
        },
    },
    i18n: {
        messages: {
            fr: {
                mySavedFilters: "Mes filtres sauvegardés",
                noFilter: "Aucun filtre pour le moment",
                savedFilters: "Filtres",
                howToAddFilters:
                    "Sélectionner un ou plusieurs filtres avant de pouvoir les sauvegarder.",
            },
            en: {
                mySavedFilters: "My saved filters",
                noFilter: "No filter for now",
                savedFilters: "Filters",
                howToAddFilters: "Select one or more filters before you can save them.",
            },
        },
    },
}
</script>
