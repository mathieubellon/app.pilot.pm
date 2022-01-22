<template>
<div class="ProjelDetailHierarchy">
    <div
        v-if="usingIE"
        v-html="$t('usingIE')"
        class="container mx-auto bg-purple-100 p-5 rounded border border-purple-300 mb-10 text-base text-purple-800 font-bold flex items-center"
    />

    <Loadarium :name="['fetchItemsForHierarchy', 'fetchProjel', 'fetchInitialData']">
        <!-- Top bar with BigFilter,
        buttons to create folder/item in the hierarchy root,
        and buttons to open/close all folders -->
        <div
            class="container bg-white mx-auto px-4 pt-3 pb-2 mb-4 border border-gray-200 rounded flex flex-col lg:flex-row items-start"
        >
            <div class="flex flex-col mb-2 lg:mb-0 justify-start flex-grow w-full">
                <BigFilter
                    :apiSource="apiSource"
                    :filterSchemaUrl="`/api/big_filter/schema/items/list/?context=${context}`"
                />
            </div>

            <div class="flex w-full h-full lg:w-auto lg:flex-shrink-0 mb-2 lg:mb-0 lg:ml-2">
                <button
                    class="button flex-1"
                    @click="openAllFolders()"
                >
                    {{ $t("openAll") }}
                </button>

                <button
                    class="button ml-2 flex-1"
                    @click="closeAllFolders()"
                >
                    {{ $t("closeAll") }}
                </button>
            </div>

            <div class="flex w-full h-full lg:w-auto lg:flex-shrink-0 mb-2 lg:mb-0 lg:ml-2">
                <AdminButton
                    aClass="button is-blue flex-1"
                    @click="createFolder(virtualRootFolder)"
                >
                    {{ $t("createFolder") }}
                </AdminButton>

                <button
                    class="button is-blue ml-2 flex-1"
                    @click="startAddItemInFolder(virtualRootFolder)"
                >
                    {{ $t("newContent") }}
                </button>
            </div>
        </div>

        <!-- Main Hierarchy box -->
        <div class="container bg-white mx-auto border border-gray-200 rounded">
            <!-- Container for the hierarchy scroller -->
            <div
                v-show="!isHierarchyEmpty"
                class="w-full"
                :class="{
                    'bg-indigo-100': rootIsHighlighted,
                }"
            >
                <!-- The scroller -->
                <!-- /!\ BIG FAT WARNING : The height of this scroller is set by the scrollerHeight data.
                It is computed dynamically in this.setScrollerStyle().
                This computation assume that the scroller goes from its top position to the bottom of the page.
                If you modify some html or css here, this code may breaks.
                Please ensure that all features related to scroll and positioning still works after any modification here.
                -->
                <RecycleScroller
                    v-slot="{ item: node, index: nodeIndex }"
                    class="px-4 py-2"
                    :style="{ height: scrollerHeight }"
                    :items="flattenedVisibleNodes"
                    :itemSize="NODE_HEIGHT"
                    keyField="nodeId"
                    typeField="type"
                >
                    <div class="flex flex-auto">
                        <!-- Rulers for nodes inside folders -->
                        <div
                            v-for="level in node.level"
                            class="flex-shrink-0 w-10 flex justify-start pl-1"
                        >
                            <span class="ProjelDetailHierarchy__ruler" />
                        </div>

                        <div class="flex-auto py-1 truncate">
                            <!-- The  box for the node-->
                            <div
                                class="flex-auto h-10 border border-gray-300 rounded px-2 flex items-stretch"
                                :class="{
                                    'bg-white': node.type == NODE_TYPES.item,
                                    'bg-gray-50': node.type == NODE_TYPES.folder,
                                    'bg-indigo-100':
                                        dropTargetFolder == node &&
                                        dropSourceNode != node &&
                                        dropSourceNode.parent != node &&
                                        !hasDescendant(dropSourceNode, dropTargetFolder),
                                    'bg-blue-200 border-blue-300 text-blue-700':
                                        node == highlightedNode,
                                }"
                                @dblclick="toggleFolder(node)"
                            >
                                <!-- Open/Close Folder -->
                                <a
                                    v-if="node.type == NODE_TYPES.folder"
                                    class="flex items-center"
                                    @click.stop="toggleFolderOpening(node)"
                                >
                                    <Icon
                                        class="text-blue-400 mr-2"
                                        :name="node.isOpen ? 'ChevronDown' : 'ChevronRight'"
                                        size="24px"
                                    />
                                </a>

                                <!-- Node representation. This is the draggable element.

                                The nodeIndex attr is necessary to retrieve the node object during drag events

                                'outline-none' is here to cancel the automatic outline added by chrome
                                on elements with tabIndex, which are added by vu-virtual-scroller.-->
                                <div
                                    class="flex flex-auto items-center truncate outline-none"
                                    :class="{
                                        ProjelHierarchy__Draggable: folderInEdition != node,
                                    }"
                                    :nodeIndex="nodeIndex"
                                >
                                    <!-- Folder representation -->
                                    <template v-if="node.type == NODE_TYPES.folder">
                                        <!-- Folder icon -->
                                        <Icon
                                            class="text-gray-400 mr-2 flex-shrink-0 fill-current"
                                            name="Folder"
                                            size="20px"
                                        />

                                        <!-- Folder name edition -->
                                        <template v-if="folderInEdition == node">
                                            <input
                                                v-model="nameEdited"
                                                class="nameEditionInput font-medium max-w-lg px-3"
                                                :class="{ 'is-invalid': folderValidationError }"
                                                ref="nameEditionInput"
                                                @blur="endNameEdition"
                                                @keyup.enter="endNameEdition"
                                            />
                                            <!-- Folder name conflict -->
                                            <Popper
                                                v-if="folderValidationError"
                                                ref="folderValidationPopper"
                                                placement="right"
                                                triggerElementName="duplicateFolderNameTrigger"
                                            >
                                                <template #triggerElement>
                                                    <span ref="duplicateFolderNameTrigger"></span>
                                                </template>
                                                <template #content>
                                                    <span class="form__field__error">
                                                        {{ folderValidationError }}
                                                    </span>
                                                </template>
                                            </Popper>
                                        </template>

                                        <!-- Folder name display ( nominal state ) -->
                                        <div
                                            v-else
                                            class="truncate"
                                            :class="{
                                                'cursor-pointer hover:bg-blue-100':
                                                    !dropSourceNode && myPermissions.is_admin,
                                            }"
                                            style="min-width: 50px"
                                            @click.stop="startNameEdition(node)"
                                        >
                                            {{ node.name | defaultVal("N/A") }}
                                        </div>
                                    </template>

                                    <!-- Item representation -->
                                    <template v-if="node.type == NODE_TYPES.item">
                                        <!-- Item type Icon -->
                                        <ItemTypeIcon
                                            v-if="getItem(node).item_type"
                                            class="text-gray-700 h-4"
                                            :name="getItem(node).item_type.icon_name"
                                        />

                                        <!-- Item title + id display ( nominal state ) -->
                                        <span class="text-gray-500 text-sm mr-1">
                                            #{{ node.id }}
                                        </span>
                                        <router-link
                                            class="truncate hover:underline"
                                            :to="{ name: 'itemDetail', params: { id: node.id } }"
                                        >
                                            {{ getItem(node).title | defaultVal("N/A") }}
                                        </router-link>
                                    </template>
                                </div>

                                <!-- Actions ( end of line ) -->
                                <div class="flex items-center">
                                    <!-- Folder actions -->
                                    <template v-if="node.type == NODE_TYPES.folder">
                                        <!-- Number of items in the folder -->
                                        <span class="text-xs text-gray-500 mr-2">
                                            {{
                                                $tc("itemsCount", countItemsInHierarchy(node.nodes))
                                            }}
                                        </span>

                                        <!-- Create item in the folder -->
                                        <button
                                            class="button is-small mr-1 pl-1 pr-0"
                                            @click.stop="startAddItemInFolder(node)"
                                        >
                                            <Icon
                                                class="text-gray-500"
                                                name="FilePlus"
                                                size="18px"
                                            />
                                        </button>

                                        <!-- Create subfolder in the folder -->
                                        <AdminButton
                                            aClass="button is-small mr-1 pl-1 pr-0"
                                            @click="createFolder(node)"
                                            @click.native.stop
                                        >
                                            <Icon
                                                class="text-gray-500"
                                                name="FolderPlus"
                                                size="18px"
                                            />
                                        </AdminButton>

                                        <!-- Start folder deletion -->
                                        <AdminButton
                                            aClass="button is-red is-small bg-red-100 hover:bg-red-200 pl-1 pr-0"
                                            @click="startFolderDeletion(node)"
                                            @click.native.stop
                                        >
                                            <Icon
                                                class="text-gray-500"
                                                name="Trash"
                                                size="18px"
                                            />
                                        </AdminButton>
                                    </template>

                                    <!-- Item actions -->
                                    <template v-if="node.type == NODE_TYPES.item">
                                        <!-- Item state update -->
                                        <ItemStateDropdown
                                            :appendToBody="true"
                                            :item="getItem(node)"
                                            placement="auto"
                                            :showStateText="!viewportLTELarge"
                                            @saved="onItemStateChanged"
                                        />

                                        <!-- Item list actions -->
                                        <ItemListActions
                                            class="ml-2"
                                            :item="getItem(node)"
                                        />
                                    </template>
                                </div>
                            </div>
                        </div>
                    </div>
                </RecycleScroller>
            </div>

            <div
                v-if="isHierarchyEmpty"
                class="help-text max-w-2xl px-4 py-8"
            >
                <div class="help-text-title">
                    <Icon
                        class="help-text-icon"
                        name="Hierarchy"
                    />
                    <span>{{ $t("treeView") }}</span>
                </div>

                <div class="help-text-content text-lg">
                    {{ $t("hierarchyIsEmpty") }}
                </div>

                <div class="flex items-center">
                    <AdminButton
                        aClass="button is-blue flex-1"
                        @click="createFolder(virtualRootFolder)"
                    >
                        {{ $t("createFolder") }}
                    </AdminButton>
                    <span class="mx-3">
                        {{ $t("or") }}
                    </span>
                    <AdminButton
                        aClass="button is-blue flex-1"
                        @click="startAddItemInFolder(virtualRootFolder)"
                    >
                        {{ $t("newContent") }}
                    </AdminButton>
                </div>
            </div>
        </div>
    </Loadarium>

    <DeleteFolderModal
        :folderInDeletion="folderInDeletion"
        @cancel="folderInDeletion = null"
        @confirm="confirmFolderDeletion()"
    />
</div>
</template>

<script>
import _ from "lodash"
import $ from "jquery"
import Vue from "vue"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { $httpX } from "@js/ajax"
import { initialDataPromise } from "@js/bootstrap"
import { enrichLightItem } from "@js/items/itemsUtils"
import { NODE_TYPES, flattenHierarchy, countItemsInHierarchy } from "@js/hierarchy"
import ResponsiveMixin from "@components/ResponsiveMixin"
import { EVENTS, eventBus } from "@js/events"
import { getItemsChoicesApiSource } from "@js/apiSource"
import browser from "prosemirror-view/src/browser"
import PilotMixin from "@components/PilotMixin"
import ProjelHierarchyMixin from "@views/projel/detail/ProjelHierarchyMixin"

import { RecycleScroller } from "vue-virtual-scroller"
import BigFilter from "@views/bigFilter/BigFilter"
import ItemTypeIcon from "@views/itemTypes/ItemTypeIcon"
import ItemState from "@views/items/ItemState"
import ItemStateDropdown from "@views/items/ItemStateDropdown"
import ItemListActions from "@views/items/list/ItemListActions"
import DeleteFolderModal from "./DeleteFolderModal"
import AdminButton from "@components/admin/AdminButton"

export default {
    name: "ProjelDetailHierarchy",
    mixins: [PilotMixin, ResponsiveMixin, ProjelHierarchyMixin],
    components: {
        RecycleScroller,
        BigFilter,
        ItemTypeIcon,
        ItemState,
        ItemStateDropdown,
        ItemListActions,
        DeleteFolderModal,
        AdminButton,
    },
    data: () => ({
        scrollerHeight: 0,

        NODE_TYPES,
        countItemsInHierarchy,
    }),
    computed: {
        ...mapGetters("projelDetail", ["projelId", "isChannelRoute", "isProjectRoute"]),

        usingIE() {
            return browser.ie
        },

        context() {
            return this.isChannelRoute ? "channel" : "project"
        },

        flattenedVisibleNodes() {
            return flattenHierarchy(this.hierarchy).filter(
                // To be visible, a node must be in an opened folder
                (node) =>
                    node.parent.isOpen &&
                    // Also, hide items that are filtered out by the BigFilter
                    (node.type == NODE_TYPES.folder || this.items[node.id]),
            )
        },

        apiSource() {
            return getItemsChoicesApiSource()
        },
    },
    methods: {
        ...mapActions("projelDetail", ["fetchProjel"]),

        /***********************
         * Items management
         ************************/

        startAddItemInFolder(folder) {
            this.parentFolderForAddItem = folder
            this.openOffPanel("addItem")
        },

        removeItemsById(nodes, itemIds) {
            for (let node of nodes) {
                if (node.type == NODE_TYPES.item) {
                    if (itemIds.includes(node.id)) {
                        this.removeNode(node)
                    }
                }
                if (node.type == NODE_TYPES.folder) {
                    this.removeItemsById(node.nodes, itemIds)
                }
            }
        },

        /***********************
         * Item handlers
         ************************/

        onItemCreated(item) {
            if (!this.parentFolderForAddItem) {
                return
            }

            this.items[item.id] = item
            let itemNode = {
                type: NODE_TYPES.item,
                id: item.id,
            }
            this.addNode(itemNode, this.parentFolderForAddItem)
            this.openFolder(this.parentFolderForAddItem)
            this.saveHierarchy()
            this.scrollToNode(itemNode)
            this.parentFolderForAddItem = null
            this.highlightedNode = itemNode
            this.stopNodeHighlightingAtNextClick(itemNode)
        },

        onItemBulkTrashed({ itemIds }) {
            this.removeItemsById(this.hierarchy, itemIds)
            // No need to save the hierarchy here, the backend will update it
        },

        onItemBulkCopied({ itemIds }) {
            this.reloadHierarchy()
        },

        onItemBulkRemovedFromProjel({ itemIds }) {
            this.removeItemsById(this.hierarchy, itemIds)
            // No need to save the hierarchy here, the backend will update it
        },

        onItemStateChanged(item) {
            this.items[item.id] = item
        },

        /***********************
         * Init
         ************************/

        fetchItemsForHierarchy() {
            let params = _.cloneDeep(this.apiSource.queryParamSerializer.params)
            if (this.isChannelRoute) {
                params.channels = this.projelId
            } else if (this.isProjectRoute) {
                params.project = this.projelId
            }

            return $httpX({
                commit: this.$store.commit,
                name: "fetchItemsForHierarchy",
                method: "GET",
                url: this.apiSource.endpoint,
                params,
            }).then((response) => response.data)
        },

        /**
        /!\ BIG FAT WARNING : The height of the scroller is set by the scrollerHeight data.
        It is computed dynamically here.
        This computation assume that the scroller goes from its top position to the bottom of the page.
        If you modify some code here, the scroller may break.
        Please ensure that all features related to scroll and positioning still works after any modification here.
        */
        setScrollerStyle() {
            let container = $(".vue-recycle-scroller__item-wrapper")

            // vue-virtual-scroller doesn't give a hook to customize the wrapper class,
            // so we bruteforce it with jquery.
            // 'outline-none' is here to cancel the automatic outline added by chrome
            // on elements with tabIndex, which are added by vu-virtual-scroller.
            container.addClass("outline-none").attr("id", "ProjelHierarchy__DragContainer")

            // Compute scroller height from the container position and the screen height
            let containerTop = container.offset().top
            // Keep 1em (=16px) of margin before the bottom of the page
            this.scrollerHeight = $(window).height() - containerTop - 16 + "px"
        },

        loadHierarchy() {
            /**
             * We need to handle all those cases :
             * - Browser open on the hierarchy page
             * - User navigate to the hierarchy page from another ProjectDetail tab
             * - Hierarchy reloading
             */
            let fetchItemsPromise = this.fetchItemsForHierarchy()
            Promise.all([this.lastFetchProjelPromise, fetchItemsPromise, initialDataPromise]).then(
                ([projel, items, initialData]) => {
                    for (let item of items) {
                        enrichLightItem(item)
                        Vue.set(this.items, item.id, item)
                    }

                    this.initHierarchy(this.projel.hierarchy)
                    this.openAllFolders()

                    // We need an initialized hierarchy to get the correct container top position
                    this.$nextTick(() => {
                        this.setScrollerStyle()
                        this.setupDraggable()
                    })
                },
            )
        },

        reloadHierarchy() {
            this.items = {}
            this.fetchProjel({ resetBeforeFetch: false })
            this.loadHierarchy()
        },
    },
    watch: {
        "apiSource.url"() {
            this.reloadHierarchy()
        },
    },
    created() {
        eventBus.on(EVENTS.itemCreated, this.onItemCreated)
        eventBus.on(EVENTS.itemBulkTrashed, this.onItemBulkTrashed)
        eventBus.on(EVENTS.itemBulkCopied, this.onItemBulkCopied)
        eventBus.on(EVENTS.itemBulkRemovedFromProjel, this.onItemBulkRemovedFromProjel)
    },
    beforeRouteEnter(to, from, next) {
        next((vm) => {
            if (from.name) {
                // Moving from one tab to another : we reload the hierarchy to see fresh data
                vm.reloadHierarchy()
            } else {
                // Initial page loading : ProjelDetailApp has already fetched the projel, no need to fetch it again
                vm.loadHierarchy()
            }
        })
    },
    beforeDestroy() {
        eventBus.off(EVENTS.itemCreated, this.onItemCreated)
        eventBus.off(EVENTS.itemBulkTrashed, this.onItemBulkTrashed)
        eventBus.off(EVENTS.itemBulkCopied, this.onItemBulkCopied)
        eventBus.off(EVENTS.itemBulkRemovedFromProjel, this.onItemBulkRemovedFromProjel)
    },
    i18n: {
        messages: {
            fr: {
                closeAll: "Fermer tout",
                hierarchyIsEmpty:
                    "Cette interface vous permet d'organiser vos contenus dans une arborescence (site internet ou application par exemple). Ou pour vous organiser comme vous le souhaitez.",
                itemsCount: "Aucun contenu | 1 contenu | {count} contenus",
                openAll: "Ouvrir tout",
                usingIE:
                    "La fonctionnalité permettant de glisser déplacer des contenus ou dossiers n’est pas disponible sur ce navigateur (<a href='https://www.pilot.pm/blog/ie11/' target='_blank' class='font-bold'>voir les détails</a>)",
            },
            en: {
                closeAll: "Close all",
                itemsCount: "No content | 1 content | {count} contents",
                hierarchyIsEmpty:
                    "This interface allows you to organize your content in a tree structure (website or application for example). Or to organize your project as you wish.",
                openAll: "Open all",
                usingIE:
                    "The drag'n'drop of contents and folders is not available in this browser (<a href='https://www.pilot.pm/blog/ie11/' target='_blank' class='font-bold'>see details</a>)",
            },
        },
    },
}
</script>

<style lang="scss">
.ProjelDetailHierarchy {
    @apply p-8 bg-gray-50;
}
.ProjelDetailHierarchy__ruler {
}
</style>
