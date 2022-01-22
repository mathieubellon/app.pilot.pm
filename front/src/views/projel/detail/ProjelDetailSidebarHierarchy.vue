<template>
<div
    class="ProjelDetailSideBar__panel"
    :class="{
        'bg-indigo-100': rootIsHighlighted,
    }"
>
    <div class="ProjelDetailSideBar__panelHeader">
        <div class="ProjelDetailSideBar__panelTitle">{{ $t("treeView") }}</div>
        <div>
            <AdminButton
                aClass="button is-small mb-1"
                @click="createFolder(virtualRootFolder)"
            >
                {{ $t("createFolder") }}
            </AdminButton>
        </div>
    </div>

    <div id="ProjelHierarchy__DragContainer">
        <div
            v-for="(folder, nodeIndex) in flattenedVisibleNodes"
            class="flex flex-auto h-7"
        >
            <!-- Rulers for nodes inside folders -->
            <div
                v-for="level in folder.level"
                class="flex-shrink-0 w-4 flex justify-start pl-1"
            >
                <span class="ProjelDetailSidebarHierarchy__ruler" />
            </div>

            <div class="flex-auto truncate">
                <div
                    class="flex-auto h-6 border border-gray-300 rounded px-1 flex items-stretch bg-gray-50"
                    :class="{
                        'hover:bg-purple-100': !dropSourceNode,
                    }"
                >
                    <!--
                    This is the draggable element.
                    The nodeIndex attr is necessary to retrieve the node object during drag events
                     -->
                    <div
                        class="flex flex-auto items-center truncate cursor-pointer"
                        :class="{
                            'bg-indigo-100':
                                dropTargetFolder == folder &&
                                dropSourceNode != folder &&
                                dropSourceNode.parent != folder &&
                                !hasDescendant(dropSourceNode, dropTargetFolder),
                            ProjelHierarchy__Draggable: folderInEdition != folder,
                            flex: dropSourceNode != folder,
                            hidden: dropSourceNode == folder,
                        }"
                        :nodeIndex="nodeIndex"
                        @click="filterOnFolder(folder)"
                    >
                        <Icon
                            class="text-gray-400 fill-current mr-1"
                            name="Folder"
                            size="16px"
                        />

                        <!-- Folder name edition -->
                        <template v-if="folderInEdition == folder">
                            <input
                                v-model="nameEdited"
                                class="nameEditionInput font-bold max-w-lg"
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
                        >
                            {{ folder.name | defaultVal("N/A") }}
                        </div>
                    </div>

                    <!-- Actions ( end of line ) -->
                    <div class="flex items-center overflow-hidden">
                        <!-- Create subfolder in the folder -->
                        <AdminButton
                            aClass="button is-xsmall pl-1 pr-0 py-0"
                            @click="createFolder(folder)"
                            @click.native.stop
                        >
                            <Icon
                                class="text-gray-500"
                                name="FolderPlus"
                                size="16px"
                            />
                        </AdminButton>

                        <!-- Edit folder name -->
                        <AdminButton
                            aClass="button is-xsmall pl-1 pr-0 py-0"
                            @click="startNameEdition(folder)"
                            @click.native.stop
                        >
                            <Icon
                                class="text-gray-500"
                                name="Edit"
                                size="16px"
                            />
                        </AdminButton>

                        <!-- Start folder deletion -->
                        <AdminButton
                            aClass="button is-red is-xsmall bg-red-100 hover:bg-red-200 pl-1 pr-0 py-0"
                            @click="startFolderDeletion(folder)"
                            @click.native.stop
                        >
                            <Icon
                                class="text-gray-500"
                                name="Trash"
                                size="18px"
                            />
                        </AdminButton>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <BarLoader
        v-if="!projel.id"
        :color="colors.grey500"
        :width="100"
        widthUnit="%"
    />

    <div v-if="projel.id && flattenedVisibleNodes.length == 0">
        {{ $t("noFolder") }}
    </div>

    <DeleteFolderModal
        :folderInDeletion="folderInDeletion"
        @cancel="folderInDeletion = null"
        @confirm="confirmFolderDeletion()"
    />
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { flattenHierarchy, NODE_TYPES } from "@js/hierarchy"
import PilotMixin from "@components/PilotMixin"
import ProjelHierarchyMixin from "@views/projel/detail/ProjelHierarchyMixin"

import DeleteFolderModal from "./DeleteFolderModal"
import AdminButton from "@components/admin/AdminButton"

export default {
    name: "ProjelDetailSidebarHierarchy",
    mixins: [PilotMixin, ProjelHierarchyMixin],
    components: {
        DeleteFolderModal,
        AdminButton,
    },
    computed: {
        ...mapState("itemList", ["apiSource"]),
        flattenedVisibleNodes() {
            return flattenHierarchy(this.hierarchy).filter(
                // Show only folders in this view
                (node) => node.type == NODE_TYPES.folder,
            )
        },
    },
    methods: {
        filterOnFolder(folder) {
            let folderPath = []
            while (folder.level > -1) {
                folderPath.unshift(folder.name)
                folder = folder.parent
            }
            this.apiSource.setFilter("folder", JSON.stringify(folderPath))
        },
    },
    created() {
        this.lastFetchProjelPromise.then(() => {
            this.initHierarchy(this.projel.hierarchy)
            this.setupDraggable()
        })
    },
    i18n: {
        messages: {
            fr: {
                noFolder: "Aucun dossier",
            },
            en: {
                noFolder: "No folder",
            },
        },
    },
}
</script>

<style lang="scss">
.ProjelDetailSidebarHierarchy__ruler {
    @apply bg-gray-300;
    width: 2px;
}
</style>
