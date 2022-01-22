<template>
<div class="ItemList w-full">
    <div
        v-if="
            items.length > 0 &&
            !loadingInProgress.fetchItemList &&
            !loadingInProgress.fetchListConfig
        "
        class="flex flex-grow justify-end"
    >
        <ItemOrdering
            class="mr-2"
            :value="apiSource.ordering"
            @orderingChange="apiSource.setOrdering"
        />
        <span class="mx-2">
            <ItemListColumnsConfig />
        </span>
        <Pagination
            :pagination="pagination"
            @pageChange="apiSource.setPage"
        />
    </div>

    <div
        v-if="!loadingInProgress.fetchItemList && !loadingInProgress.fetchListConfig"
        class="flex flex-col w-full rounded my-5"
    >
        <transition
            enter-active-class="animated animated-500 fadeIn"
            leave-active-class="animated animated-500 fadeOut"
            mode="out-in"
        >
            <ItemListBulkbar v-if="anySelectedForBulkAction" />

            <div
                v-else-if="items.length"
                class="ItemListHeader"
            >
                <div
                    v-if="canBulkUpdate"
                    class="ItemListCell is-checkbox is-header"
                ></div>
                <div
                    v-show="columns.itemType"
                    class="ItemListCell is-item-type is-header"
                >
                    <span class="hidden md:block">{{ $t("type") }}</span>
                </div>
                <div
                    v-show="columns.id"
                    class="ItemListCell is-id is-header"
                >
                    <span class="hidden md:block">ID</span>
                </div>
                <div
                    v-show="columns.title"
                    class="ItemListCell is-title is-header"
                >
                    {{ $t("title") }}
                </div>
                <div
                    v-show="columns.language && currentDesk.itemLanguagesEnabled"
                    class="ItemListCell is-language is-header"
                >
                    <span class="hidden lg:block">{{ $t("lang") }}</span>
                </div>
                <div
                    v-show="columns.publication && context != 'picker' && context != 'shared'"
                    class="ItemListCell is-pubdate is-header"
                >
                    <span class="hidden lg:block">{{ $t("publication") }}</span>
                </div>
                <div
                    v-show="
                        columns.project &&
                        context != 'project' &&
                        context != 'picker' &&
                        context != 'shared'
                    "
                    class="ItemListCell is-project is-header"
                >
                    <span class="hidden lg:block">{{ $t("project") }}</span>
                </div>
                <div
                    v-show="
                        columns.channels &&
                        context != 'channel' &&
                        context != 'picker' &&
                        context != 'shared'
                    "
                    class="ItemListCell is-channel is-header"
                    :class="{ channelNamesVisible: context == 'project' }"
                >
                    <span class="hidden lg:block">{{ $t("channels") }}</span>
                </div>
                <div
                    v-show="columns.state && context != 'shared'"
                    class="ItemListCell is-state is-header"
                    :class="{ tight: !canUpdateItemStatus }"
                >
                    <span class="hidden lg:block">{{ $t("state") }}</span>
                </div>
                <div
                    v-show="canBulkUpdate"
                    class="ItemListCell is-options is-header"
                ></div>
                <div
                    v-show="context == 'picker'"
                    class="ItemListCell is-header is-pick"
                ></div>
            </div>
        </transition>

        <ItemListElement
            v-for="item in items"
            :context="context"
            :item="item"
            :key="item.id"
            @itemStateChanged="onItemStateChanged"
        />
    </div>

    <div
        v-if="
            items.length > 0 &&
            !loadingInProgress.fetchItemList &&
            !loadingInProgress.fetchListConfig
        "
        class="flex flex-grow justify-end"
    >
        <Pagination
            :pagination="pagination"
            @pageChange="apiSource.setPage"
        />
    </div>

    <Loadarium :name="['fetchItemList', 'fetchListConfig', 'fetchSavedFilters']" />
</div>
</template>

<script>
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import { getMainItemListName } from "@/store/modules/ListConfigStore"
import PilotMixin from "@components/PilotMixin"

import Pagination from "@components/Pagination"
import ItemListBulkbar from "@views/items/list/ItemListBulkbar.vue"
import ItemListElement from "./ItemListElement.vue"
import ItemOrdering from "./ItemOrdering.vue"
import ItemListColumnsConfig from "./ItemListColumnsConfig.vue"

export default {
    name: "ItemList",
    mixins: [PilotMixin],
    components: {
        Pagination,
        ItemListElement,
        ItemListBulkbar,
        ItemOrdering,
        ItemListColumnsConfig,
    },
    props: {
        // Can be "trash", "shared", "project", "channel", "dashboard", "picker", or a tab name from the main item list
        context: String,
    },
    computed: {
        ...mapState("loading", ["loadingInProgress"]),
        ...mapState("itemList", ["apiSource", "items", "pagination"]),
        ...mapGetters("bulk", ["anySelectedForBulkAction"]),
        ...mapGetters("listConfig", ["itemListColumns"]),
        columns() {
            return this.itemListColumns
        },
        canBulkUpdate() {
            return (
                this.context != "picker" &&
                this.context != "trash" &&
                this.context != "shared" &&
                this.context != "dashboard"
            )
        },
        canUpdateItemStatus() {
            return this.context != "picker" && this.context != "trash" && this.context != "shared"
        },
    },
    methods: {
        ...mapMutations("itemList", ["updateItemInList"]),
        ...mapActions("listConfig", ["fetchListConfig"]),
        ...mapActions("itemList", ["fetchItemList"]),
        onItemStateChanged(item) {
            this.updateItemInList(item)
        },
    },
    watch: {
        "apiSource.url"() {
            this.fetchItemList()
        },
    },
    created() {
        this.fetchListConfig(getMainItemListName())
    },
}
</script>

<style lang="scss">
@import "~@sass/include_media.scss";
@import "~@sass/colors.scss";
@import "~@sass/business/items_vars.scss";

.ItemListHeader {
    @apply flex bg-gray-100 border border-b-0 border-gray-200 rounded-t-sm flex-row items-end flex-no-wrap justify-between h-8;
    @include ItemListHeaderHeight;
}

.ItemListCell {
    @apply min-w-0 text-sm font-medium text-gray-700 leading-tight mx-1 overflow-hidden h-8;
    @apply border border-transparent;
    @apply flex items-center;

    flex: 1 1 100%;

    a {
        @apply text-gray-900;
    }

    a:hover {
        @apply text-blue-700 underline;
    }
}

.ItemListCell.is-checkbox {
    flex-basis: 30px;
    flex-shrink: 0;
    @apply justify-center cursor-pointer mr-0;
    @include media("<=tablet") {
        @apply hidden;
    }
}

.ItemListCell.is-item-type {
    flex-basis: 35px;
    flex-shrink: 0;
    @apply justify-center mr-0;
}

.ItemListCell.is-id {
    flex-basis: 60px;
    flex-shrink: 0;
    @apply justify-center mr-0;
}

.ItemListCell.is-title {
    @apply ml-0 text-left font-medium;
    a {
        @apply truncate w-full;
    }

    .ItemListElement__titleText {
        @apply truncate;
    }
}

.ItemListCell.is-language {
    flex-basis: 32px;
    flex-shrink: 0;

    @apply justify-center cursor-pointer;
    @include media("<=phone") {
        display: none;
    }
}

.ItemListCell.is-pubdate {
    flex-basis: 80px;
    flex-shrink: 0;
    @apply justify-center cursor-pointer;

    @include media("<desktop") {
        @apply mx-0;
        flex-basis: 40px;
        flex-shrink: 0;
        justify-content: center;
    }
    @include media("<phone") {
        display: none;
    }
}

.ItemListCell.is-project {
    flex-basis: 200px;
    flex-shrink: 0;
    @apply truncate;
    transition: all 0.2s ease;
    @include media("<desktop") {
        @apply mx-0;
        flex-basis: 40px;
        flex-shrink: 0;
        justify-content: center;
    }
    @include media("<phone") {
        display: none;
    }
}

.ItemListCell.is-channel {
    flex-basis: 60px;
    flex-shrink: 0;
    @apply justify-center cursor-pointer;
    &.channelNamesVisible {
        flex-basis: 150px;
        flex-shrink: 0;
        justify-content: left;
    }

    @include media("<desktop") {
        @apply mx-0;
        flex-basis: 40px;
        flex-shrink: 0;
        justify-content: center;
        &.channelNamesVisible {
            flex-basis: 40px;
            flex-shrink: 0;
        }
    }
    @include media("<phone") {
        display: none;
    }
}

.ItemListCell.is-state {
    flex-basis: 125px;
    flex-shrink: 0;
    @apply justify-start cursor-pointer mr-0;

    &.tight {
        flex-basis: 50px;
        @apply justify-center;
    }

    @include media("<=large") {
        flex-basis: 50px;
    }
}

.ItemListCell.is-options {
    flex-basis: 30px;
    flex-shrink: 0;
    @apply justify-center cursor-pointer;
}

.ItemListCell.is-pick {
    flex-basis: 125px;
    flex-shrink: 0;
}

// .is-header is declared at the end of the <style> block, so cursor-default takes precedence
.ItemListCell.is-header {
    @apply font-sans no-underline cursor-default;
    border: none;
    background: transparent;
}
</style>
