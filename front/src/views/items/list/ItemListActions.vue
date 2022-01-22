<template>
<Popper
    :appendToBody="true"
    closeOnClickSelector=".willClose"
    placement="left"
    triggerElementName="PopperOptions"
    triggerType="click"
    :visibleArrow="true"
>
    <template #triggerElement>
        <div
            class="ItemListCell is-options"
            ref="PopperOptions"
        >
            <Icon
                class="text-gray-800 h-4"
                name="MenuDotsVertical"
            />
        </div>
    </template>

    <template #content>
        <div class="w-56">
            <button
                class="menu-item willClose"
                @click="showItemPreviewModal(item)"
            >
                <Icon
                    class="mr-4"
                    name="Eye"
                />
                {{ $t("preview") }}
            </button>

            <button
                class="menu-item willClose"
                @click="openUpdatePanel()"
            >
                <Icon
                    class="mr-4"
                    name="Edit"
                />
                {{ $t("edit") }}
            </button>

            <MenuItemWithConfirm
                iconName="Copy"
                :label="$t('duplicate')"
                loadingName="bulkAction-copy"
                @confirmed="bulkCopyItems([item.id])"
            />

            <MenuItemWithConfirm
                v-if="isChannelRoute || isProjectRoute"
                iconName="CloseCircle"
                :label="$t(isChannelRoute ? 'removeFromChannel' : 'removeFromProject')"
                loadingName="bulkAction-copy"
                @confirmed="removeItemsFromProjel({ projelId, itemIds: [item.id] })"
            />

            <MenuItemWithConfirm
                :confirmButtonText="$t('confirmDeletion')"
                :confirmTitle="$t('confirmDeletionMessage')"
                iconName="Trash"
                :isRed="true"
                :label="$t('delete')"
                loadingName="bulkAction-trash"
                @confirmed="bulkTrashItems([item.id])"
            />
        </div>
    </template>
</Popper>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import MenuItemWithConfirm from "@components/MenuItemWithConfirm"

export default {
    name: "ItemListActions",
    mixins: [PilotMixin],
    components: {
        MenuItemWithConfirm,
    },
    props: {
        item: {
            type: Object,
            required: true,
        },
    },
    computed: {
        ...mapGetters("projelDetail", ["projelId", "isChannelRoute", "isProjectRoute"]),
    },
    methods: {
        ...mapActions("itemActions", [
            "bulkTrashItems",
            "bulkCopyItems",
            "showItemPreviewModal",
            "removeItemsFromProjel",
        ]),
        ...mapMutations("bulk", ["setSingleObjectSelection"]),
        openUpdatePanel() {
            this.setSingleObjectSelection(this.item.id)
            this.openOffPanel("itemBulkUpdate")
        },
    },
    i18n: {
        messages: {
            fr: {
                removeFromChannel: "Retirer du canal",
                removeFromProject: "Retirer du projet",
            },
            en: {
                removeFromChannel: "Remove from the channel",
                removeFromProject: "Remove from the project",
            },
        },
    },
}
</script>

<style lang="scss"></style>
