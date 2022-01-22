<template>
<MainLayout>
    <template #title>
        {{ $t("assets") }}
    </template>

    <template #actions>
        <button class="button is-blue startUpload">
            {{ $t("addAsset") }}
        </button>
    </template>

    <template #content>
        <router-view class="p-0 md:p-4 md:pr-0" />
    </template>
</MainLayout>
</template>

<script>
import _ from "lodash"
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import { getAssetApiSource } from "@js/apiSource"
import MainLayout from "@components/layout/MainLayout"

export default {
    name: "AssetListApp",
    components: {
        MainLayout,
    },
    computed: {
        ...mapState("assetList", ["apiSource", "savedQuery"]),
    },
    methods: {
        ...mapMutations("assetList", ["setApiSource", "saveQuery"]),
        applySavedQuery() {
            // The query string in the url has priority over the savedQuery
            // Don't apply the savedQuery if there's already a query string in the url.
            if (!document.location.search) {
                this.apiSource.setQuery(this.savedQuery)
            }
        },
    },
    watch: {
        "apiSource.url"() {
            // The only case where apiSource query may be empty is when we land on a new page.
            // In this case we don't want to erase the saved query with our empty query.
            if (!_.isEmpty(this.apiSource.query)) {
                this.saveQuery(this.apiSource.query)
            }
        },
    },
    // Apply the saved query string when the app is created
    created() {
        this.setApiSource(getAssetApiSource())
        this.applySavedQuery()
    },
    i18n: {
        messages: {
            fr: {
                addAsset: "Ajouter des fichiers",
            },
            en: {
                addAsset: "Upload files",
            },
        },
    },
}
</script>
