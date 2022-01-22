<template>
<MainLayout :appBodyScroll="false">
    <template #title>
        <div
            v-if="wikiPage.id"
            class="flex justify-between w-full"
        >
            <span class="flex items-center truncate">
                <div class="truncate">{{ wikiPage.name }}</div>
            </span>
        </div>

        <span v-else>{{ $t("loading") }}</span>
    </template>

    <template #actions>
        <WikiTopBarActions v-if="wikiPage.id" />
    </template>

    <template #content>
        <div class="flex h-full">
            <WikiPageList />
            <transition
                enter-active-class="animated animated-150 fadeIn"
                leave-active-class="animated animated-150 fadeOut"
                mode="out-in"
            >
                <router-view :key="$route.path" />
            </transition>
        </div>
    </template>
</MainLayout>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import MainLayout from "@components/layout/MainLayout"
import WikiPageList from "./WikiPageList"
import WikiTopBarActions from "./WikiTopBarActions"

export default {
    name: "WikiApp",
    mixins: [PilotMixin],
    components: {
        MainLayout,
        WikiTopBarActions,
        WikiPageList,
    },
    computed: {
        ...mapState("wiki", ["wikiPage"]),
    },
    methods: {
        ...mapActions("wiki", ["fetchWikiPagesList"]),
    },
    created() {
        this.fetchWikiPagesList()
    },
}
</script>
