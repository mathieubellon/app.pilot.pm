<template>
<div class="ItemListForProjel">
    <BarLoader
        :color="colors.grey500"
        :loading="!isItemListReady"
        :width="100"
        widthUnit="%"
    />

    <template v-if="isItemListReady">
        <div class="flex justify-between">
            <div class="font-bold text-gray-800 text-lg py-2 mb-2">
                {{ $t("items") }}

                <span
                    v-if="folder"
                    class="text-base text-purple-800 bg-purple-200 px-1 py-1 inline-flex flex-no-wrap items-center"
                >
                    <Icon
                        class="text-purple-800 fill-current mr-1"
                        name="Folder"
                        size="14px"
                    />

                    <span>{{ folder }}</span>

                    <button
                        class="button is-xsmall is-white ml-3 p-0 pl-1"
                        @click="apiSource.removeFilter('folder')"
                    >
                        <Icon
                            name="Close"
                            size="16px"
                        />
                    </button>
                </span>
            </div>

            <div class="flex-shrink-0">
                <button
                    v-if="currentRouteName == 'channelDetail-contents'"
                    class="button"
                    @click="toggleSidebarHierarchyVisibility()"
                >
                    <!-- The empty span is required to correctly align with flex display -->
                    <span>
                        <Icon
                            class="text-gray-600"
                            name="Hierarchy"
                        />
                    </span>
                    {{ $t("toggleHierarchy") }}
                </button>
                <button
                    v-if="
                        currentRouteName === 'projectDetail-informations' ||
                        currentRouteName === 'channelDetail-informations' ||
                        currentRouteName === 'projectDetail-contents' ||
                        currentRouteName === 'channelDetail-contents'
                    "
                    class="button is-blue"
                    @click="openOffPanel('addItem')"
                >
                    {{ $t("newContent") }}
                </button>
            </div>
        </div>

        <BigFilter
            :apiSource="apiSource"
            :filterSchemaUrl="`/api/big_filter/schema/items/list/?context=${context}`"
        />

        <ItemList
            class="mt-2"
            :context="context"
        />

        <template v-if="items.length == 0 && isItemListReady">
            <div
                v-if="apiSource.hasFilter"
                class="text-gray-800 font-bold text-center p-1O bg-gray-50 my-2 py-2"
            >
                {{ $t("noResults") }}
            </div>
            <div
                v-else
                class="max-w-2xl mx-auto my-10"
            >
                <ItemHelpText />
            </div>
        </template>
    </template>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"
import {
    getItemListForChannelName,
    getItemListForProjectName,
} from "@/store/modules/ListConfigStore"
import { getItemsForChannelApiSource, getItemsForProjectApiSource } from "@js/apiSource"

import BigFilter from "@views/bigFilter/BigFilter"
import ItemList from "@views/items/list/ItemList.vue"
import ItemHelpText from "@views/items/list/ItemHelpText"

export default {
    name: "ItemListForProjel",
    mixins: [PilotMixin],
    components: {
        BigFilter,
        ItemList,
        ItemHelpText,
    },
    data: () => ({
        listConfigName: null,
        isItemListReady: false,
    }),
    computed: {
        ...mapState("projelDetail", ["projel"]),
        ...mapGetters("projelDetail", ["projelId", "isChannelRoute", "isProjectRoute"]),
        ...mapState("itemList", ["apiSource", "items"]),
        folder() {
            let folderParam = this.apiSource.query.folder
            if (!folderParam) {
                return null
            }
            let folders = JSON.parse(folderParam)
            return folders.join(" / ")
        },
        context() {
            return this.isChannelRoute ? "channel" : "project"
        },
    },
    methods: {
        ...mapMutations("itemList", ["setApiSource"]),
        ...mapActions("projelDetail", ["toggleSidebarHierarchyVisibility"]),
        ...mapActions("listConfig", ["fetchListConfig", "partialUpdateListConfig"]),
        ...mapActions("itemList", ["fetchItemList"]),
        onOrderingChange(ordering) {
            // Do not fetch items until the component is ready
            if (this.isItemListReady) {
                this.apiSource.setOrdering(ordering)
                this.saveOrdering()
            }
        },
        saveOrdering() {
            this.partialUpdateListConfig({
                name: this.listConfigName,
                listConfig: { ordering: this.apiSource.ordering },
            })
        },
    },
    created() {
        if (this.isChannelRoute) {
            this.setApiSource(getItemsForChannelApiSource(this.projelId))
            this.listConfigName = getItemListForChannelName(this.projelId)
        } else if (this.isProjectRoute) {
            this.setApiSource(getItemsForProjectApiSource(this.projelId))
            this.listConfigName = getItemListForProjectName(this.projelId)
        }

        this.fetchListConfig(this.listConfigName).then((listConfig) => {
            // Set the ordering defined by the listConfig
            if (listConfig.ordering && listConfig.ordering !== this.ordering) {
                // Setting the ordering here will trigger the watcher on ordering,
                // which will in turn fetch the items.
                this.apiSource.setOrdering(listConfig.ordering)
            }

            // Now that we have an ordering, we can fetch the items
            this.fetchItemList().then(() => {
                this.isItemListReady = true
            })
        })
    },
    i18n: {
        messages: {
            fr: {
                toggleHierarchy: "Voir dossiers",
            },
            en: {
                toggleHierarchy: "See folders",
            },
        },
    },
}
</script>

<style lang="scss">
.ItemListForProjel {
    @apply py-2 px-4 bg-white rounded border border-gray-200;
}
</style>
