<template>
<div class="ItemListBulkbar">
    <BulkBar
        :instances="items"
        :pagination="pagination"
        :queryParams="apiSource.query"
    >
        <div class="flex flex-row items-center mb-1">
            <Popper
                closeOnClickSelector=".willClose, .confirmAction"
                triggerElementName="ItemListBulkbarPopper"
                triggerType="click"
            >
                <template #triggerElement>
                    <button
                        class="button is-small is-outlined is-white"
                        ref="ItemListBulkbarPopper"
                        type="button"
                    >
                        {{ $t("selectAction") }}

                        <!-- The empty span is required to correctly align with flex display -->
                        <span>
                            <Icon
                                class="caret"
                                name="ChevronDown"
                            />
                        </span>
                    </button>
                </template>

                <template #content>
                    <div class="w-56">
                        <button
                            class="menu-item willClose"
                            @click="openOffPanel('itemBulkUpdate')"
                        >
                            <Icon
                                class="mr-4"
                                name="Edit"
                            />
                            {{ $t("edit") }}
                        </button>

                        <MenuItemWithConfirm
                            :confirmTitle="$tc('confirmCopyTitle', itemIds.length)"
                            iconName="Copy"
                            :label="$t('duplicate')"
                            loadingName="bulkAction-copy"
                            @confirmed="bulkCopyItems(itemIds)"
                        />

                        <MenuItemWithConfirm
                            v-if="isChannelRoute || isProjectRoute"
                            iconName="CloseCircle"
                            :label="$t(isChannelRoute ? 'removeFromChannel' : 'removeFromProject')"
                            loadingName="bulkAction-copy"
                            @confirmed="removeItemsFromProjel({ projelId, itemIds })"
                        />

                        <MenuItemWithConfirm
                            :confirmButtonText="$t('confirmDeletion')"
                            :confirmTitle="$tc('confirmDeletionTitle', itemIds.length)"
                            iconName="Trash"
                            :isRed="true"
                            :label="$t('delete')"
                            loadingName="bulkAction-trash"
                            @confirmed="bulkTrashItems(itemIds)"
                        />
                    </div>
                </template>
            </Popper>
        </div>
    </BulkBar>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"
import ResponsiveMixin from "@components/ResponsiveMixin"

import BulkBar from "@components/BulkBar.vue"
import MenuItemWithConfirm from "@components/MenuItemWithConfirm"

export default {
    name: "ItemListBulkbar",
    mixins: [PilotMixin, ResponsiveMixin],
    components: {
        BulkBar,
        MenuItemWithConfirm,
    },
    computed: {
        ...mapState("itemList", ["apiSource", "pagination", "items"]),
        ...mapGetters("projelDetail", ["projelId", "isChannelRoute", "isProjectRoute"]),
        ...mapGetters("bulk", ["bulkActionSelectionAsList"]),
        itemIds() {
            return this.bulkActionSelectionAsList
        },
    },
    methods: {
        ...mapMutations("itemList", ["removeItemsById"]),
        ...mapActions("bulk", ["bulkAction"]),
        ...mapActions("itemActions", ["bulkCopyItems", "bulkTrashItems", "removeItemsFromProjel"]),
    },
    i18n: {
        messages: {
            fr: {
                confirmCopyTitle:
                    "Confirmer la copie du contenu | Confirmer la copie des {count} contenus",
                confirmDeletionTitle:
                    "Confirmer la suppression du contenu | Confirmer la suppresion de {count} contenus",
                removeFromChannel: "Retirer du canal",
                removeFromProject: "Retirer du projet",
                selectAction: "Choisir une action...",
            },
            en: {
                confirmCopyTitle: "Confirm copy of this content | Confirm copy of {count} contents",
                confirmDeletionTitle:
                    "Confirm deletion of 1 content | Confirm deletion of {count} contents",
                removeFromChannel: "Remove from the channel",
                removeFromProject: "Remove from the project",
                selectAction: "Select action...",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/business/items_vars.scss";

.ItemListBulkbar {
    @apply sticky top-0 bg-gray-50 border-b-2 border-gray-300;
    @include ItemListHeaderHeight;

    // Align exactly the checkbox with those into the list
    .BulkBar {
        margin-left: 14px;
    }
}
</style>
