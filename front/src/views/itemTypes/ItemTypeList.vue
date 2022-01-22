<template>
<div>
    <Loadarium name="fetchItemTypes">
        <AdminList
            :instancesList="sortedItemTypes"
            :showActions="myPermissions.is_admin"
            :sortable="false"
            @delete="deleteItemType"
            @deletionCancelled="cancelItemTypeDeletion"
            @deletionRequested="onDeletionRequested"
            @edit="goToItemTypeEdition"
        >
            <div
                class="flex items-center"
                slot-scope="{ instance }"
            >
                <template v-if="itemTypeInDeletion != instance">
                    <ItemTypeIcon :name="instance.icon_name" />
                    <div class="flex flex-col ml-4">
                        <span class="font-bold">
                            {{ instance.name }}
                        </span>
                        <span class="text-normal text-gray-600">
                            {{ instance.description }}
                        </span>
                    </div>

                    <a
                        v-if="!myPermissions.is_admin"
                        @click="goToItemTypeEdition(instance)"
                    >
                        {{ $t("details") }}
                    </a>
                </template>

                <div
                    v-else
                    class="text-red-500"
                >
                    {{ $t("itemTypeDeletionWarning") }}
                    <br />
                    {{ $t("deleteItemType") }} "{{ instance.name }}" (
                    {{
                        $tc("linkedItemsCount", instance.linked_item_count || 0, {
                            linkedItemsCount: instance.linked_item_count || 0,
                        })
                    }}
                    ) ?
                </div>
            </div>
        </AdminList>
    </Loadarium>

    <div class="help-text">
        <div class="help-text-title">
            <Icon
                class="help-text-icon"
                name="File"
            />
            <span>{{ $t("howItemTypesWorks") }}</span>
        </div>

        <div class="help-text-content">{{ $t("explainItemType") }}</div>
    </div>

    <AutoFormInPanel
        name="itemTypeForm"
        ref="form"
        :saveUrl="urls.itemTypes"
        :schema="itemTypeFormSchema"
        :title="$t('addItemType')"
        @created="onItemTypeCreated"
    />
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { sortByAlphaString } from "@js/utils.js"
import PilotMixin from "@components/PilotMixin"
import FullLayout from "@components/layout/FullLayout"
import ItemTypeFormSchemaMixin from "./ItemTypeFormSchemaMixin.vue"
import ItemTypeIcon from "@views/itemTypes/ItemTypeIcon"
import AdminList from "@components/admin/AdminList.vue"

export default {
    name: "ItemTypeList",
    mixins: [PilotMixin, ItemTypeFormSchemaMixin],
    components: {
        AdminList,
        FullLayout,
        ItemTypeIcon,
    },
    data: () => ({
        // Item type asked for deletion, waiting confirmation
        itemTypeInDeletion: null,
    }),
    computed: {
        ...mapState("itemTypes", ["itemTypes"]),
        ...mapGetters("users", ["myPermissions"]),
        sortedItemTypes() {
            return sortByAlphaString(this.itemTypes, (itemType) => itemType.name)
        },
    },
    methods: {
        ...mapActions("itemTypes", ["deleteItemType"]),
        onItemTypeCreated(itemType) {
            this.itemTypes.unshift(itemType)
        },
        goToItemTypeEdition(itemType) {
            this.$router.push({ name: "itemTypesEdit", params: { id: itemType.id } })
        },
        onDeletionRequested(itemType) {
            this.itemTypeInDeletion = itemType
        },
        cancelItemTypeDeletion(state) {
            this.itemTypeInDeletion = null
        },
    },
    i18n: {
        messages: {
            fr: {
                addItemType: "Ajouter un type de contenu",
                deleteItemType: "Supprimer le type de contenu",
                explainItemType:
                    "En tant qu’administrateur vous pouvez créer les types de contenus que vous souhaitez et qualifier vos contenus de manière avancée avec des formulaires personnalisables.",
                howItemTypesWorks: "Les types de contenu ?",
                itemTypeDeletionWarning:
                    "Attention la suppression d'un type de contenu entraine la suppression des contenus associés",
                linkedItemsCount:
                    "{linkedItemsCount} contenu associé | {linkedItemsCount} contenus associés",
            },
            en: {
                addItemType: "Add an item type",
                deleteItemType: "Delete the item type",
                explainItemType:
                    "As an administrator you can create the types of content you want and qualify your content in an advanced way with customizable forms.",
                howItemTypesWorks: "Item Types ?",
                itemTypeDeletionWarning:
                    "Warning, deleting an item type will also delete the associated items",
                linkedItemsCount:
                    "{linkedItemsCount} associated content | {linkedItemsCount} associated contents",
            },
        },
    },
}
</script>
