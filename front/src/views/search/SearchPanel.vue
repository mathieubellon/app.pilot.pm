<template>
<MainLayout>
    <template slot="title">
        {{ $t("search") }}
    </template>

    <div
        class="p-2 md:p-8 md:pr-4 h-full"
        slot="content"
    >
        <div class="border border-gray-200 rounded bg-white p-4">
            <div class="flex items-center">
                <input
                    class="bg-gray-100"
                    ref="searchInput"
                    placeholder="Saisissez votre recherche"
                    type="search"
                    v-model.trim="query"
                />
            </div>

            <div class="flex items-center">
                <SearchHowTo />
                <a
                    v-if="query"
                    class="SearchPanel__inputWrapper__clear"
                    @click.prevent="clear"
                >
                    {{ $t("delete") }}
                </a>
            </div>

            <div v-if="query">
                <div class="tabs mt-10">
                    <a
                        :class="['tab', { 'is-active': currentTab == 'items' }]"
                        @click.prevent="currentTab = 'items'"
                    >
                        <span>{{ $t("contents") }}</span>
                        &nbsp;( {{ itemsCount }} )
                    </a>

                    <a
                        :class="['tab', { 'is-active': currentTab == 'projects' }]"
                        @click.prevent="currentTab = 'projects'"
                    >
                        <span>{{ $t("projects") }}</span>
                        &nbsp;( {{ projectsCount }} )
                    </a>
                </div>

                <div class="SearchPanel__tabsContent">
                    <!-- Item results Tab -->
                    <div
                        v-if="currentTab == 'items'"
                        :class="['SearchPanelTabs__panel', { 'is-active': itemsCount > 0 }]"
                        key="itemsTab"
                    >
                        <SearchResultTab
                            :docTypeData="this.items"
                            :hitDisplayComponent="SearchItemHitDisplay"
                            @loadMoreButton="search('items', true)"
                        />
                    </div>

                    <!-- Project results Tab -->
                    <div
                        v-if="currentTab == 'projects'"
                        :class="['SearchPanelTabs__panel', { 'is-active': projectsCount > 0 }]"
                        key="projectsTab"
                    >
                        <SearchResultTab
                            :docTypeData="this.projects"
                            :hitDisplayComponent="SearchProjectHitDisplay"
                            @loadMoreButton="search('projects', true)"
                        />
                    </div>
                </div>
            </div>

            <div v-else>
                <div
                    v-if="searchHistory.length > 0"
                    class="SearchPanel__history"
                >
                    <div class="SearchPanel__history__header">{{ $t("searchHistory") }}</div>
                    <div
                        v-for="historyQuery in searchHistory"
                        class="SearchPanel__historyElement"
                    >
                        <a
                            class="SearchPanel__historyElementQuery"
                            @click.prevent="query = historyQuery"
                        >
                            {{ historyQuery }}
                        </a>
                        <a
                            class="SearchPanel__historyElementRemove"
                            @click.prevent="removeHistoryElement(historyQuery)"
                        >
                            <Icon
                                class="text-gray-500 w-5"
                                name="Close"
                            />
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</MainLayout>
</template>

<script>
import _ from "lodash"
import $ from "jquery"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import { LocalStorageWrapper } from "@js/localStorage.js"
import PilotMixin from "@components/PilotMixin"
import MainLayout from "@components/layout/MainLayout"

import SearchHowTo from "./SearchHowTo"
import SearchResultTab from "./SearchResultTab"
import SearchItemHitDisplay from "./SearchItemHitDisplay"
import SearchProjectHitDisplay from "./SearchProjectHitDisplay"

const ITEMS_DOC_TYPE = "items"
const PROJECTS_DOC_TYPE = "projects"
const HISTORY_SIZE = 15

let localHistory = new LocalStorageWrapper("SearchPanel.history")

function createDocTypeData() {
    return {
        filteredUsers: [],
        pagination: null,
        showLoading: false,
        error: null,
    }
}

export default {
    name: "SearchPanel",
    mixins: [PilotMixin],
    components: {
        SearchHowTo,
        SearchResultTab,
        MainLayout,
    },
    data: () => ({
        query: null,
        currentTab: ITEMS_DOC_TYPE,
        items: createDocTypeData(),
        projects: createDocTypeData(),
        searchHistory: [],
        SearchItemHitDisplay: SearchItemHitDisplay,
        SearchProjectHitDisplay: SearchProjectHitDisplay,
    }),
    computed: {
        itemsCount() {
            return this.items.showLoading ? "?" : _.get(this, "items.pagination.total_results", "?")
        },
        projectsCount() {
            return this.projects.showLoading
                ? "?"
                : _.get(this, "projects.pagination.total_results", "?")
        },
    },
    watch: {
        query() {
            this.items.showLoading = true
            this.projects.showLoading = true
            this.freshSearch()
        },
    },
    methods: {
        clear() {
            this.query = null
        },
        // Debounce by 1500ms, so multiple keystrokes in the query input don't trigger an avalanche of API calls
        freshSearch: _.debounce(function () {
            this.search(ITEMS_DOC_TYPE)
            this.search(PROJECTS_DOC_TYPE)
        }, 1500),
        search(docType, append = false) {
            // No search if the query is empty
            if (!this.query) {
                return
            }

            let page = append ? this[docType].pagination.next : 1
            this[docType].error = null

            // Send the query to the backend
            $httpX({
                name: "search",
                commit: this.$store.commit,
                method: "get",
                url: urls.search.format({ docType }),
                params: {
                    query: this.query,
                    page: page,
                },
            })
                .then((response) => {
                    this[docType].pagination = _.omit(response.data, "hits")

                    if (append)
                        this[docType].filteredUsers = this[docType].filteredUsers.concat(
                            response.data.hits,
                        )
                    else this[docType].filteredUsers = response.data.hits

                    this[docType].showLoading = false
                    // Update the history and push it into the window.localStorage

                    // If it exists, remove the latest query from the history
                    _.pull(this.searchHistory, this.query)
                    // Put the latest query at the top of the history
                    this.searchHistory.unshift(this.query)
                    // Limit the history to 10 elements
                    this.searchHistory.splice(HISTORY_SIZE)
                    // Save the history to the window.localStorage
                    localHistory.set(this.searchHistory)
                })
                .catch((error) => {
                    this[docType].error = error.response
                    this[docType].showLoading = false
                })
        },
        removeHistoryElement(query) {
            // If it exists, remove the query from the history
            // Use _.without instead of _.pull to trigger Vue reactivity
            this.searchHistory = _.without(this.searchHistory, query)
            // Save the history to the window.localStorage
            localHistory.set(this.searchHistory)
        },
    },
    created() {
        let savedHistory = localHistory.get()
        if (savedHistory) {
            this.searchHistory = savedHistory
        }
    },
    mounted() {
        $(this.$refs.searchInput).focus()
    },
    i18n: {
        messages: {
            fr: {
                search: "Recherche",
                contents: "Contenus",
                projects: "Projets",
                searchHistory: "Historique de vos recherches",
            },
            en: {
                search: "Search",
                contents: "Contents",
                projects: "Projects",
                searchHistory: "Your search history",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.SearchPanel__inputWrapper__clear {
    @apply text-gray-600 underline text-sm ml-2;
}

.SearchPanel__history {
    @apply flex flex-col mt-10;
}
.SearchPanel__history__header {
    @apply text-gray-900 font-bold mb-2;
}
.SearchPanel__historyElement {
    @apply flex items-center -mx-2 py-1 px-2 flex justify-between w-full rounded;
    &:hover {
        @apply bg-gray-50;
    }
}
.SearchPanel__historyElementQuery {
    @apply text-gray-900 w-full;
}

.SearchPanel__historyElementRemove {
    cursor: pointer;
    margin-left: 5px;
}
</style>
