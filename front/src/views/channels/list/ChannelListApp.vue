<template>
<MainLayout>
    <template slot="title">{{ $t("channels") }}</template>

    <ChannelTabs slot="middlebar" />

    <template #actions>
        <button
            v-if="$route.name === 'channelList-active'"
            class="button is-blue"
            @click.prevent="openOffPanel('addChannelForm')"
        >
            {{ $t("newChannel") }}
        </button>
    </template>

    <template #content>
        <router-view class="p-2 md:p-8 md:pr-4" />
    </template>
</MainLayout>
</template>

<script>
import _ from "lodash"
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import { getChannelApiSource } from "@js/apiSource"
import PilotMixin from "@components/PilotMixin"

import MainLayout from "@components/layout/MainLayout"
import ChannelTabs from "./ChannelTabs"

export default {
    name: "ChannelListApp",
    mixins: [PilotMixin],
    components: {
        MainLayout,
        ChannelTabs,
    },
    data: () => ({
        lastFetchRouteName: null,
    }),
    computed: {
        ...mapState("channelList", ["apiSource", "savedQueries"]),
    },
    methods: {
        ...mapMutations("channelList", ["setApiSource", "saveQuery"]),
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
    },
    // Apply the saved query string when the app is created
    created() {
        this.setApiSource(getChannelApiSource())
        this.applySavedQuery()
    },
    i18n: {
        messages: {
            fr: {
                newChannel: "Nouveau canal",
            },
            en: {
                newChannel: "New channel",
            },
        },
    },
}
</script>
