<template>
<div class="tabs">
    <router-link
        class="tab"
        active-class="is-active"
        :to="{ name: 'itemList-active' }"
    >
        {{ $t("actives") }}
    </router-link>

    <router-link
        v-if="lastSelectedSavedFilter && lastSelectedSavedFilter.type == 'list'"
        class="tab"
        active-class="is-active"
        :to="{ name: 'itemList-filter', params: { id: lastSelectedSavedFilter.id } }"
    >
        {{ lastSelectedSavedFilter.title }}
    </router-link>

    <SavedFiltersPopper type="list" />
    <router-link
        class="tab"
        active-class="is-active"
        :to="{ name: 'itemList-trash' }"
    >
        {{ $t("trash") }}
    </router-link>
</div>
</template>

<script>
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"

import PilotMixin from "@components/PilotMixin"
import SavedFiltersPopper from "@views/savedFilters/SavedFiltersPopper"

export default {
    name: "ItemListTabs",
    mixins: [PilotMixin],
    components: {
        SavedFiltersPopper,
    },
    computed: {
        ...mapState("savedFilter", ["lastSelectedSavedFilter"]),
    },
    methods: {},
    i18n: {
        messages: {
            fr: {
                actives: "Actifs",
                trash: "Corbeille",
            },
            en: {
                actives: "Actives",
                trash: "Trash",
            },
        },
    },
}
</script>
