<template>
<div class="ItemListWithBigFilter">
    <div
        v-if="isInternalSharedSavedFilter"
        class="alert-panel is-yellow"
    >
        {{ $t("internalSharedFilterMessage", { creator: selectedSavedFilter.user.username }) }}
    </div>

    <BigFilter
        :apiSource="apiSource"
        :canSave="true"
        filterSchemaUrl="/api/big_filter/schema/items/list/"
    />

    <!--
    <div
        v-if="currentRouteName == 'itemList-filter'"
        class="flex w-full h-full md:w-auto md:flex-shrink-0 mb-2 md:mb-0 md:ml-2"
    >
        <SavedFilterActions />
    </div>
    -->

    <!-- Transform 'itemList-trash' in 'trash'-->
    <ItemList :context="currentRouteName.replace('itemList-', '')" />

    <template
        v-if="
            items.length == 0 &&
            !loadingInProgress.fetchItemList &&
            !loadingInProgress.fetchListConfig
        "
    >
        <div
            v-if="apiSource.hasFilter"
            class="text-gray-800 font-bold text-center p-1O bg-gray-100 rounded"
        >
            {{ $t("noResults") }}
        </div>
        <ItemHelpText v-else />
    </template>

    <ItemAddPanel />

    <SavedFilterCreateUpdatePanel
        :filtersQueryString="apiSource.queryString"
        :isCalendar="false"
    />

    <SavedFilterInternalSharePanel />

    <SavedFilterDeletePanel goToAfterDelete="itemList-active" />

    <SharingsModal
        :sharingTarget="{
            type: 'list',
            saved_filter_id: savedFilterId,
        }"
    />
</div>
</template>

<script>
import { mapActions, mapGetters, mapMutations, mapState } from "vuex"
import PilotMixin from "@components/PilotMixin"

import BigFilter from "@views/bigFilter/BigFilter"
import Pagination from "@components/Pagination"
import SavedFilterCreateUpdatePanel from "@views/savedFilters/SavedFilterCreateUpdatePanel.vue"
import SavedFilterInternalSharePanel from "@views/savedFilters/SavedFilterInternalSharePanel.vue"
import SavedFilterDeletePanel from "@views/savedFilters/SavedFilterDeletePanel.vue"
import SharingsModal from "@views/sharings/internal/SharingsModal"

import ItemList from "./ItemList"
import ItemHelpText from "./ItemHelpText"
import ItemAddPanel from "../ItemAddPanel.vue"
import ItemListColumnsConfig from "./ItemListColumnsConfig.vue"

export default {
    name: "ItemListWithBigFilter",
    mixins: [PilotMixin],
    components: {
        BigFilter,
        Pagination,
        SavedFilterCreateUpdatePanel,
        SavedFilterInternalSharePanel,
        SavedFilterDeletePanel,
        SharingsModal,

        ItemList,
        ItemHelpText,
        ItemAddPanel,
        ItemListColumnsConfig,
    },
    computed: {
        ...mapState("loading", ["loadingInProgress"]),
        ...mapState("itemList", ["items", "pagination", "apiSource"]),
        ...mapGetters("savedFilter", [
            "savedFilterId",
            "selectedSavedFilter",
            "isInternalSharedSavedFilter",
            "isFilterTabOpen",
        ]),
        ...mapGetters(["currentRouteName"]),
    },
    methods: {
        ...mapMutations("itemList", [
            "setQueryParamsFromBigFilter",
            "setQueryParamsFromQueryString",
            "setOrdering",
            "setPagination",
        ]),
        ...mapActions("itemList", ["fetchItemList"]),
        ...mapActions("savedFilter", ["fetchSavedFilters"]),
    },
    created() {
        // If we're loading a filter view,
        // we must wait for the filter query before loading the items
        if (this.isFilterTabOpen) {
            this.fetchSavedFilters().then(() => {
                this.fetchItemList()
            })
        } else {
            this.fetchItemList()
        }
    },
    i18n: {
        messages: {
            fr: {
                internalSharedFilterMessage:
                    "Ce filtre a été partagé par @{creator}. Vous pouvez le copier dans vos filtres personnels.",
            },
            en: {
                internalSharedFilterMessage:
                    "This filter has been shared by @{creator}. You can copy it into your personnal filters.",
            },
        },
    },
}
</script>
