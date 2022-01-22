<template>
<div
    class="WikiPageList w-48 md:w-64 ml-0 md:ml-8 flex-shrink-0 bg-gray-50 border-r border-gray-300 overflow-y-auto xl:w-full max-w-xs"
>
    <Loadarium name="fetchWikiPagesList">
        <div class="py-4 pr-2">
            <VueFuse
                class="is-white"
                :defaultAll="true"
                :keys="['name']"
                :list="sortedWikiPages"
                :placeholder="$t('search')"
                :shouldSort="false"
                :threshold="0.1"
                @result="onFuseResult"
            />
        </div>
        <div class="border border-gray-200 mr-2">
            <template v-for="wikiPageItem in filteredWikiPages">
                <SmartLink
                    class="WikiPageLink"
                    :class="{
                        'bg-white text-blue-800': wikiPage.id == wikiPageItem.id,
                        'border-b-0': wikiPage.id == wikiPageItem.id && headingNodes.length,
                    }"
                    :key="wikiPageItem.id"
                    :to="wikiPageItem.url"
                >
                    {{ wikiPageItem.name }}
                </SmartLink>

                <div
                    v-if="wikiPage.id == wikiPageItem.id && headingNodes.length"
                    class="py-1 text-sm font-medium bg-white text-blue-800 border-b border-gray-200"
                >
                    <a
                        v-for="(headingNode, headingIndex) in headingNodes"
                        class="block hover:underline w-full text-blue-800 font-medium pl-3 mb-2 leading-tight"
                        @click.stop="scrollToHeading(headingIndex)"
                    >
                        &rarrfs; {{ headingNode.content[0].text }}
                    </a>
                </div>
            </template>
        </div>
    </Loadarium>
</div>
</template>

<script>
import $ from "jquery"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { getHeadingNodes } from "@richText/utils"
import PilotMixin from "@components/PilotMixin"
import { sortByAlphaString } from "@js/utils"

export default {
    name: "WikiPageList",
    mixins: [PilotMixin],
    data: () => ({
        filteredWikiPages: [],
    }),
    computed: {
        ...mapState("wiki", ["wikiPagesList", "wikiPage"]),
        homePage() {
            return this.wikiPagesList.find((wikiPage) => wikiPage.is_home_page)
        },
        sortedWikiPages() {
            let sorted = sortByAlphaString(
                this.wikiPagesList.filter((wikiPage) => !wikiPage.is_home_page),
                (wikiPage) => wikiPage.name,
            )
            return this.homePage ? [this.homePage, ...sorted] : sorted
        },
        headingNodes() {
            return getHeadingNodes(this.wikiPage.content)
        },
    },
    methods: {
        onFuseResult(filteredWikiPages) {
            this.filteredWikiPages = filteredWikiPages
        },
        scrollToHeading(headingIndex) {
            let $WikiPage = $(".WikiPage")
            let heading = $WikiPage.find("h1,h2,h3,h4,h5,h6").get(headingIndex)
            let topCoord =
                $(heading).offset().top - // Position relative to the document
                $WikiPage.offset().top + // Adjust for the container position
                $WikiPage.scrollTop() // Adjust for the container scroll
            $WikiPage.scrollTop(topCoord)
        },
    },
}
</script>

<style lang="scss">
.WikiPageLink {
    @apply py-2 text-base font-semibold flex text-black items-center px-3 border-b border-gray-200;

    &:hover {
        @apply text-blue-800 bg-white;
    }
    &:last-child {
        @apply border-b-0;
    }
}
</style>
