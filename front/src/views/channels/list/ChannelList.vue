<template>
<div class="ChannelList">
    <BigFilter
        :apiSource="apiSource"
        filterSchemaUrl="/api/big_filter/schema/channels/list/"
        :placeholder="$t('channelBigFilterPlaceholder')"
    />

    <div
        v-if="channels.length > 0 && !loadingInProgress.fetchChannelList"
        class="flex flex-grow justify-end"
    >
        <OrderingSelector
            defaultOrdering="-updated_at"
            :orderings="orderings"
            :value="apiSource.ordering"
            @orderingChange="apiSource.setOrdering"
        />

        <Pagination
            class="ml-2"
            :pagination="pagination"
            @pageChange="apiSource.setPage"
        />
    </div>

    <div class="my-5">
        <Loadarium name="fetchChannelList" />

        <transition-group
            v-if="!loadingInProgress.fetchChannelList"
            enter-active-class="animated fadeInUp"
            leave-active-class="animated fadeOutLeft"
        >
            <ChannelListElement
                v-for="channel in channels"
                :channel="channel"
                :key="channel.id"
            />
        </transition-group>

        <template v-if="channels.length == 0 && !loadingInProgress.fetchChannelList">
            <div
                v-if="apiSource.hasFilter"
                class="text-gray-800 font-bold text-center p-10 bg-gray-50 rounded"
            >
                {{ $t("noResults") }}
            </div>
            <ChannelHelpText v-else />
        </template>
    </div>

    <div
        v-if="channels.length > 0 && !loadingInProgress.fetchChannelList"
        class="flex flex-grow justify-end"
    >
        <Pagination
            :pagination="pagination"
            @pageChange="apiSource.setPage"
        />
    </div>

    <OffPanel name="addChannelForm">
        <div slot="offPanelTitle">{{ $t("newChannel") }}</div>
        <ChannelFormAdd slot="offPanelBody"></ChannelFormAdd>
    </OffPanel>
</div>
</template>

<script>
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import PilotMixin from "@components/PilotMixin"

import BigFilter from "@views/bigFilter/BigFilter"
import OrderingSelector from "@views/bigFilter/OrderingSelector"
import Pagination from "@components/Pagination"
import ChannelListElement from "./ChannelListElement"
import ChannelHelpText from "./ChannelHelpText"
import ChannelFormAdd from "./ChannelFormAdd"

export default {
    name: "ChannelList",
    mixins: [PilotMixin],
    components: {
        BigFilter,
        OrderingSelector,
        Pagination,
        ChannelListElement,
        ChannelHelpText,
        ChannelFormAdd,
    },
    computed: {
        ...mapState("channelList", ["channels", "pagination", "apiSource"]),
        ...mapState("loading", ["loadingInProgress"]),
        orderings() {
            return [
                { value: "name", label: this.$t("sortByNameAsc") },
                { value: "-name", label: this.$t("sortByNameDesc") },
                { value: "updated_at", label: this.$t("sortByUpdateDateAsc") },
                { value: "-updated_at", label: this.$t("sortByUpdateDateDesc") },
                { value: "created_at", label: this.$t("sortByCreatedDateAsc") },
                { value: "-created_at", label: this.$t("sortByCreatedDateDesc") },
            ]
        },
    },
    methods: {
        ...mapActions("channelList", ["fetchChannelList"]),
    },
    watch: {
        "apiSource.url"() {
            this.fetchChannelList()
        },
    },
    created() {
        this.fetchChannelList()
    },
    i18n: {
        messages: {
            fr: {
                channelBigFilterPlaceholder: "Rechercher dans les canaux",
                sortByCreatedDateAsc: "Date de création la plus ancienne en premier",
                sortByCreatedDateDesc: "Date de création la plus récente en premier",
                sortByUpdateDateAsc: "Date de mise à jour la plus ancienne en premier",
                sortByUpdateDateDesc: "Date de mise à jour la plus récente en premier",
                sortByNameAsc: "Nom, A->Z",
                sortByNameDesc: "Nom, Z->A",
            },
            en: {
                channelBigFilterPlaceholder: "Search the channels",
                sortByCreatedDateAsc: "Creation date, oldest first",
                sortByCreatedDateDesc: "Creation date, newest first",
                sortByNameAsc: "Name, A->Z",
                sortByNameDesc: "Name, Z->A",
                sortByUpdateDateAsc: "Updated date, oldest first",
                sortByUpdateDateDesc: "Updated date, newest first",
            },
        },
    },
}
</script>
