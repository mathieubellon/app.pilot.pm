<template>
<div
    class="DrawerHistoryElement relative"
    :class="{
        active: editSession.version == itemReadOnly.version,
        diffing: editSession == editSessionForDiff,
        major: isMajorVersion,
    }"
    @click="showEditSession({ editSession, withDiff: isDiffModeActive })"
>
    <!-- We need a click.stop to prevent propagation -->
    <!-- checkbox -->
    <div
        class="p-2 mr-2"
        @click.stop
    >
        <input
            class="form-checkbox h-6 w-6 cursor-pointer text-indigo-600"
            :checked="isDiffCheckboxChecked"
            type="checkbox"
            @change="onDiffCheckboxInput"
        />
    </div>

    <!-- Infos -->
    <div class="flex flex-col flex-grow w-full">
        <!-- Version number + loader -->
        <div>
            <span
                class="text-gray-800 text-sm font-semibold"
                :class="{
                    'text-base': isMajorVersion,
                }"
            >
                {{ $t("version") }} {{ editSession.version }}
            </span>
            <span
                v-if="editSession.restored_from_version"
                class="text-xs text-indigo-700"
            >
                {{ $t("restoredFromVersion") }} {{ editSession.restored_from_version }}
            </span>
        </div>

        <!-- date + authors -->
        <div>
            <span class="text-gray-600 text-xs">
                {{ editSession.end | dateTimeFormatShort }}
            </span>

            <Popper
                triggerElementName="PopperAuthors"
                triggerType="hover"
                :visibleArrow="false"
            >
                <template #triggerElement>
                    <!-- We need a click.stop to prevent propagation -->
                    <div
                        class="inline-flex flex-wrap max-w-xs overflow-hidden bg-gray-50 rounded border border-gray-100 leading-tight cursor-pointer hover:bg-blue-50"
                        ref="PopperAuthors"
                        @click.stop
                    >
                        <div
                            v-if="editor"
                            v-for="editor in editSession.editors.slice(0, 2)"
                            class="mr-1 text-gray-700"
                            :key="editor.id"
                        >
                            <UserDisplay
                                v-if="editor.id"
                                :user="editor"
                                :withAvatar="false"
                                :withUsername="true"
                            />
                            <template v-else>{{ editor }}</template>
                        </div>
                        <a
                            v-if="editSession.editors.length > 2"
                            class="ml-1"
                        >
                            ...&nbsp;+{{ editSession.editors.length - 2 }}
                        </a>
                    </div>
                </template>

                <template #content>
                    <div
                        v-if="editor"
                        v-for="editor in editSession.editors"
                        @click.stop
                    >
                        <UserDisplay
                            v-if="editor.id"
                            :user="editor"
                            :withAvatar="false"
                            :withUsername="true"
                        />
                        <template v-else>{{ editor }}</template>
                    </div>
                </template>
            </Popper>
        </div>
    </div>

    <!-- Menu -->
    <!-- .stop needed on @click to prevent version loading -->
    <div
        :class="{
            'mr-2': isMajorVersion,
        }"
        @click.stop
    >
        <Popper
            closeOnClickSelector=".willClose"
            triggerElementName="PopperVersion"
            triggerType="click"
            :visibleArrow="false"
        >
            <template #triggerElement>
                <button
                    class="text-gray-900 p-2 hover:bg-gray-100 rounded"
                    ref="PopperVersion"
                    @click
                >
                    <Icon
                        class="text-gray-900"
                        name="MenuDotsHorizontal"
                    />
                </button>
            </template>

            <template #content>
                <div class="w-48">
                    <MenuItemWithConfirm
                        v-if="canRestore(editSession)"
                        :confirmMessage="$t('confirmRestoration')"
                        :label="$t('restore')"
                        loadingName="itemRestore"
                        @confirmed="restore(editSession)"
                    />

                    <ItemExportDropdown :sessionId="editSession.id" />

                    <button
                        v-if="!isCurrentVersion(editSession.version)"
                        class="menu-item willClose"
                        @click="showMergeToolWithSnapshot(editSession)"
                    >
                        {{ $t("openMergeTool") }} V{{ editSession.version }} -> V{{ item.version }}
                    </button>
                </div>
            </template>
        </Popper>
    </div>

    <div
        v-if="editSession.version == versionCurrentlyLoading"
        class="absolute bottom-0 inset-x-0"
    >
        <BarLoader
            :color="colors.grey700"
            :width="100"
            widthUnit="%"
        />
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import MenuItemWithConfirm from "@components/MenuItemWithConfirm"
import ItemExportDropdown from "./ItemExportDropdown"

export default {
    name: "DrawerHistoryElement",
    mixins: [PilotMixin],
    components: {
        MenuItemWithConfirm,
        ItemExportDropdown,
    },
    props: {
        editSession: Object,
    },
    computed: {
        ...mapState("itemDetail", [
            "item",
            "itemReadOnly",
            "versionCurrentlyLoading",
            "editSessionForDiff",
            "exitingDiffMode",
        ]),
        ...mapGetters("itemDetail", [
            "isCurrentVersion",
            "isDiffModeActive",
            "canRestore",
            "getMinorVersion",
        ]),
        isDiffCheckboxChecked() {
            return (
                !this.exitingDiffMode &&
                this.isDiffModeActive &&
                (this.editSession.version == this.itemReadOnly.version ||
                    this.editSession == this.editSessionForDiff)
            )
        },
        isMajorVersion() {
            return this.getMinorVersion(this.editSession) == 0
        },
    },
    methods: {
        ...mapActions("itemDetail", [
            "showEditSession",
            "restore",
            "showSessionContent",
            "showSessionDiff",
            "showMergeToolWithSnapshot",
            "exitDiffMode",
        ]),
        onDiffCheckboxInput() {
            // Click on an checked diff checkbox : exit diff mode
            if (this.isDiffCheckboxChecked) {
                this.exitDiffMode()
            }

            // Click on an unchecked diff checkbox, during diff mode : change the diffed version
            else if (this.isDiffModeActive) {
                this.showEditSession({
                    editSessionForDiff: this.editSession,
                    withDiff: true,
                })
            }

            // Click on an unchecked diff checkbox, outside diff mode : start a diff with this edit session as reference
            else {
                this.showEditSession({
                    editSession: this.editSession,
                    withDiff: true,
                })
            }
        },
    },
    i18n: {
        messages: {
            fr: {
                authors: "Auteurs",
                by: "Par",
                cancelRestore: "Annuler 'Restaurer'",
                compareWithVersion: "Comparer avec cette version",
                confirmRestoration: "Confirmer 'Restaurer'",
                openMergeTool: "Diff interactif",
                restore: "Restaurer",
                restoredFromVersion: "Restaurée depuis la",
            },
            en: {
                authors: "Authors",
                by: "By",
                cancelRestore: "Cancel 'Restore'",
                compareWithVersion: "Compare with this version",
                confirmRestoration: "Confirm 'Restore'",
                openMergeTool: "Interactive diff",
                restore: "Restore",
                restoredFromVersion: "Restored from version",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.DrawerHistoryElement {
    @apply flex items-center bg-white rounded border border-gray-300 p-3 pl-0 mb-3;

    &.major {
        @apply border-indigo-400 border-2 -ml-4 -mr-4 p-5 pl-4;
    }

    &.active {
        @apply bg-indigo-300;
    }

    &.diffing {
        @apply bg-indigo-100;
    }

    &:hover {
        @apply cursor-pointer bg-indigo-200;
    }
}
</style>
