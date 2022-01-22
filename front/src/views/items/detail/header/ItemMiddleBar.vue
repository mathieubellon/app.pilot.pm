<template>
<div
    v-if="item.user_has_access"
    class="ItemMiddleBar"
>
    <div class="flex">
        <div class="flex flex-col flex-grow">
            <ItemMiddleBarTabs />
        </div>
        <div
            v-if="viewportGTEPhone"
            class="flex items-center justify-end"
        >
            <ItemRealtimeUsers />
        </div>
    </div>
</div>
</template>

<script>
import { mapState, mapGetters } from "vuex"
import PilotMixin from "@components/PilotMixin"
import ResponsiveMixin from "@components/ResponsiveMixin"

import ItemMiddleBarTabs from "./ItemMiddleBarTabs"
import ItemRealtimeUsers from "@views/items/detail/header/ItemRealtimeUsers"

export default {
    name: "ItemMiddleBar",
    mixins: [PilotMixin, ResponsiveMixin],
    components: {
        ItemMiddleBarTabs,
        ItemRealtimeUsers,
    },
    computed: {
        ...mapState("itemDetail", ["item"]),
        ...mapGetters("itemDetail", ["itemId"]),
    },
    i18n: {
        messages: {
            fr: {
                infos: "infos",
                loadingMenu: "Chargement du menu ...",
                loading: "Chargement",
            },
            en: {
                infos: "infos",
                loadingMenu: "Loading menu ..",
                loading: "Chargement",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors";
@import "~@sass/include_media.scss";

.ItemMiddleBar {
    @apply flex flex-col flex-grow;
    @include media("<=tablet") {
        @apply flex-col;
    }
}
</style>
