<template>
<div class="ItemAddPanel">
    <OffPanel
        name="addItem"
        width="40%"
    >
        <div slot="offPanelTitle">{{ $t("selectItemType") }}</div>
        <div slot="offPanelBody">
            <template v-if="!usageLimitReached('items')">
                <button
                    v-for="itemType in itemTypes"
                    class="flex bg-gray-50 border border-gray-200 hover:bg-gray-100 text-left w-full rounded mb-3 p-2"
                    @click="selectItemType(itemType)"
                >
                    <ItemTypeIcon
                        class="mr-4 flex-shrink-0 text-gray-700 mt-1"
                        :name="itemType.icon_name"
                    />
                    <div class="flex flex-col justify-center">
                        <div class="flex-shrink-0 font-bold text-base">
                            {{ itemType.name }}
                        </div>
                        <div class="text-sm text-gray-500 text-sm leading-tight">
                            {{ itemType.description }}
                        </div>
                    </div>
                </button>

                <SmartLink
                    class="flex bg-gray-50 border border-gray-200 hover:bg-gray-100 text-left w-full rounded mb-3 p-2 text-blue-500"
                    :to="urls.itemTypesApp.url"
                >
                    <Icon
                        class="mr-4 flex-shrink-0 text-blue-500 mt-1"
                        name="PlusCircle"
                    />
                    <div class="flex flex-col justify-center">
                        <div class="flex-shrink-0 font-bold text-base">
                            {{ $t("createItemType") }}
                        </div>
                    </div>
                </SmartLink>
            </template>

            <UsageLimitAlert usageLimitName="items" />
        </div>
    </OffPanel>
    <OffPanel
        name="addItemForm"
        :stretched="true"
        width="40%"
    >
        <div slot="offPanelTitle">
            {{ $t("newContentWithType") }} {{ itemType && itemType.name }}
        </div>

        <template slot="offPanelBody">
            <template v-if="copy === null">
                <ItemAddForm
                    :initialChannel="initialChannel"
                    :initialItemData="copiedFrom"
                    :initialProject="initialProject"
                    :itemType="itemType"
                    @saved="onItemSaved"
                />
            </template>

            <div
                v-else
                class="p-4"
            >
                <p class="mb-8 text-green-500 font-bold text-lg">
                    ✓ {{ $t("copyCreated") }} : {{ copy.title }}
                </p>
                <div class="flex justify-between">
                    <SmartLink
                        class="button is-blue w-1/2 mr-4"
                        :to="copy.url"
                    >
                        {{ $t("goToCopiedContent") }}
                    </SmartLink>
                    <a
                        class="button is-outlined w-1/2"
                        @click="closeForm"
                    >
                        {{ $t("closePanel") }}
                    </a>
                </div>
            </div>
        </template>
    </OffPanel>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { EVENTS, dispatchEvent } from "@js/events"
import PilotMixin from "@components/PilotMixin"

import ItemTypeIcon from "@views/itemTypes/ItemTypeIcon"
import UsageLimitAlert from "@components/UsageLimitAlert.vue"
import ItemAddForm from "./ItemAddForm.vue"

export default {
    name: "ItemAddPanel",
    mixins: [PilotMixin],
    components: {
        ItemAddForm,
        ItemTypeIcon,
        UsageLimitAlert,
    },
    props: {
        copiedFrom: Object,
        initialProject: Object,
        initialChannel: Object,
    },
    data: () => ({
        itemType: null,
        copy: null,
    }),
    computed: {
        ...mapState("itemTypes", ["itemTypes"]),
        ...mapGetters("usageLimits", ["usageLimitReached"]),
    },
    methods: {
        selectItemType(itemType) {
            this.itemType = itemType
            this.openOffPanel("addItemForm")
            this.closeOffPanel("addItem")
        },
        onItemSaved(item) {
            dispatchEvent(EVENTS.itemCreated, item)
            this.$emit("created", item)

            // Item copy context
            if (this.copiedFrom) {
                this.copy = item
            }
            // Item list context
            else {
                setTimeout(() => {
                    this.closeForm()
                }, 1000)
            }
        },
        closeForm() {
            this.copy = null
            this.closeOffPanel("addItemForm")
        },
    },
    i18n: {
        messages: {
            fr: {
                copyCreated: "Contenu copié avec succès",
                createItemType: "Créer et personnaliser un type de contenu",
                goToCopiedContent: "Aller au contenu copié",
                newContentWithType: "Nouveau contenu de type",
                selectItemType: "Sélectionnez le type de contenu que vous souhaitez créer",
            },
            en: {
                copyCreated: "Copy successfully created",
                createItemType: "Create and customize an item type",
                goToCopiedContent: "Go to the copied content",
                newContentWithType: "New item of type",
                selectItemType: "Select the type of content you want to create",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";
.ItemAddPanel__ItemType {
    margin-bottom: 0.3em;
    padding: 0.3em 0.2em;
    background-color: #fefefe;
    a {
        text-decoration: none;
        color: $blue;
    }
}

.ItemAddPanel__ItemType:hover {
    background-color: $gray-lighter;
    border-radius: 5px;
}

.ItemAddPanel__ItemType__name {
    font-weight: 600;
}

.ItemAddPanel__ItemType__description {
    color: $gray;
    font-size: 0.9em;
}
</style>
