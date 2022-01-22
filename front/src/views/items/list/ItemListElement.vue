<template>
<div
    class="ItemListElement"
    :class="[
        context,
        {
            selected: isSelectedForBulkAction,
        },
    ]"
>
    <!--Select toggle-->
    <div
        v-if="canBulkUpdate"
        class="ItemListCell is-checkbox"
        @click="toggleForBulkAction(item)"
    >
        <input
            :checked="isSelectedForBulkAction"
            type="checkbox"
        />
    </div>

    <!--Item Type -->
    <div
        v-show="columns.itemType && context != 'shared'"
        class="ItemListCell is-item-type"
    >
        <ItemTypeIcon
            v-if="item.item_type"
            class="text-gray-700 h-4"
            :name="item.item_type.icon_name"
        />
    </div>

    <!--ID -->
    <div
        v-show="columns.id"
        class="ItemListCell is-id text-gray-500 w-20 text-center"
    >
        #{{ item.id }}
    </div>

    <!--Title -->
    <div
        v-show="columns.title"
        class="ItemListCell is-title"
    >
        <Popper
            v-if="item.is_private"
            placement="right"
            triggerElementName="PopperIsPrivate"
            triggerType="hover"
        >
            <template #triggerElement>
                <span ref="PopperIsPrivate">
                    <Icon
                        class="text-red-700 w-4"
                        name="LockClosed"
                    />
                </span>
            </template>

            <template #content>
                <div v-if="!item.user_has_access">{{ $t("itemLockedAndYouHaveNoAccess") }}</div>
                <div v-else>{{ $t("itemLockedAndYouCanAccess") }}</div>
            </template>
        </Popper>

        <div
            v-if="context == 'picker'"
            @click="showItemPreviewModal(item)"
        >
            <div class="ItemListElement__titleText">
                {{ item.title ? item.title : $t("untitled") }}
            </div>
        </div>
        <SmartLink
            v-else
            :to="item.url"
        >
            <div
                class="ItemListElement__titleText"
                :title="item.title"
            >
                {{ item.title ? item.title : $t("untitled") }}
            </div>
        </SmartLink>

        <!--<div class="Item__searchResults" v-html="item.search_headline" ></div>-->
    </div>

    <!--Language -->
    <div
        v-show="columns.language && currentDesk.itemLanguagesEnabled"
        class="ItemListCell is-language"
    >
        <Popper
            placement="top"
            triggerElementName="LangPopper"
            triggerType="click"
        >
            <template #triggerElement>
                <div ref="LangPopper">
                    <Icon
                        class="mx-1 sm:mx-0 w-4"
                        :class="item.language ? 'text-gray-500 sm:hidden' : 'text-gray-200'"
                        name="Language"
                    />
                    <span
                        v-if="item.language"
                        class="sm:m-0 inline-flex items-center p-1 rounded-sm bg-gray-100 text-gray-600"
                    >
                        {{ languageCode }}
                    </span>
                </div>
            </template>
            <template #content>
                <div class="font-semibold text-sm text-gray-900">
                    {{ $t("itemLanguage") }}
                </div>
                <span
                    v-if="item.language"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium leading-4 bg-gray-100 text-gray-800"
                >
                    {{ getChoiceDisplay("languagesChoices", item.language) }}
                </span>
                <span v-else>
                    {{ $t("thisItemHasNoLanguageSet") }}
                </span>
            </template>
        </Popper>
    </div>

    <!--Publication date-->
    <div
        v-show="columns.publication && context != 'picker' && context != 'shared'"
        class="ItemListCell is-pubdate"
    >
        <DatePickerPopper
            :naiveTime="true"
            placement="bottom"
            triggerElementName="PopperRef"
            :value="item.publication_dt"
            @input="onPublicationDateInput"
        >
            <template #triggerElement>
                <div ref="PopperRef">
                    <Loadarium :name="`updateItemPublicationDate${item.id}`">
                        <Icon
                            class="mx-1 sm:mx-0 flex-shrink-0 lg:hidden w-4"
                            :class="item.publication_dt ? 'text-gray-500' : 'text-gray-100'"
                            name="Calendar"
                        />
                        <a
                            v-if="item.publication_dt"
                            class="hidden lg:flex font-mono"
                        >
                            {{ item.publication_dt | dateFormat }}
                        </a>
                        <a
                            v-else
                            class="hidden lg:flex text-gray-300"
                        >
                            -
                        </a>
                    </Loadarium>
                </div>
            </template>

            <template #message>
                <template v-if="item.publication_dt">
                    <div class="flex items-center text-gray-700">
                        {{ $t("publicationDate") }}
                    </div>
                    <div class="font-black">
                        {{ item.publication_dt | dateFormat }}
                    </div>
                </template>
                <div
                    v-else
                    class="text-black font-black"
                >
                    {{ $t("noPublicationDate") }}
                </div>
            </template>
        </DatePickerPopper>
    </div>

    <!--Project-->
    <div
        v-show="
            columns.project && context != 'project' && context != 'picker' && context != 'shared'
        "
        class="ItemListCell is-project"
    >
        <Icon
            class="mx-1 sm:mx-0 flex-shrink-0 lg:hidden w-4"
            :class="item.project ? 'text-gray-500' : 'text-gray-200'"
            name="Project"
        />
        <SmartLink
            v-if="item.project"
            class="hidden lg:flex truncate"
            :to="item.project.url"
        >
            {{ item.project.name }}
        </SmartLink>
        <div
            v-else
            class="hidden lg:flex text-gray-300"
        >
            -
        </div>
    </div>

    <!--Channels-->
    <div
        v-show="
            columns.channels && context != 'channel' && context != 'picker' && context != 'shared'
        "
        class="ItemListCell is-channel"
        :class="{ channelNamesVisible: context === 'project' }"
    >
        <Popper
            placement="top"
            triggerElementName="PopperChannels"
            triggerType="click"
            :visibleArrow="true"
        >
            <template #triggerElement>
                <div
                    class="truncate"
                    ref="PopperChannels"
                >
                    <Icon
                        v-if="context !== 'project'"
                        class="mx-1 sm:mx-0 flex-shrink-0 w-4"
                        :class="item.channels.length > 0 ? 'text-gray-500' : 'text-gray-200'"
                        name="Channel"
                    />
                    <div
                        v-if="item.channels.length > 0"
                        class="truncate"
                        :class="{ 'sm:hidden': context !== 'project' }"
                    >
                        {{ channelNames }}
                    </div>
                    <div
                        v-else
                        class="text-gray-300"
                        :class="{ 'sm:hidden': context !== 'project' }"
                    >
                        {{ $t("noChannel") }}
                    </div>
                </div>
            </template>

            <template #content>
                <div class="w-64">
                    <div v-if="item.channels.length > 0">
                        <div class="font-semibold text-sm text-gray-900">
                            {{ $t("channels") }}
                        </div>
                        <SmartLink
                            v-for="channel in item.channels"
                            class="flex items-center cursor-pointer bg-gray-100 border border-gray-300 rounded p-2 mr-1 mt-1"
                            :key="channel.id"
                            :to="channel.url"
                        >
                            <Icon
                                class="flex-shrink-0 w-4 hover:text-teal-600"
                                :class="
                                    item.channels.length > 0 ? 'text-gray-500' : 'text-gray-200'
                                "
                                name="Channel"
                            />
                            <div class="truncate">
                                {{ channel.name }}
                            </div>
                        </SmartLink>
                    </div>
                    <div v-else>
                        {{ $t("noChannel") }}
                    </div>
                </div>
            </template>
        </Popper>
    </div>

    <!--States-->
    <div
        v-show="columns.state && context != 'shared'"
        class="ItemListCell is-state"
        :class="{ tight: !canUpdateItemStatus }"
    >
        <Icon
            v-if="item.in_trash"
            class="text-red-400"
            name="Trash"
            size="18px"
        />
        <ItemStateDropdown
            v-else-if="canUpdateItemStatus"
            :inactiveMentionGroups="inactiveMentionGroups"
            :item="item"
            placement="auto"
            :showStateText="!viewportLTELarge"
            @saved="$emit('itemStateChanged', $event)"
        />
        <ItemState
            v-else
            :showStateText="false"
            :state="item.workflow_state"
        />
    </div>

    <!--Options menu-->
    <ItemListActions
        v-if="canBulkUpdate"
        :item="item"
    />

    <!-- ItemPicker action-->
    <div
        v-if="context == 'picker'"
        class="ItemListCell is-pick"
    >
        <BarLoader
            v-if="isLoadingLink"
            class="w-full"
        />
        <span
            v-else-if="isItemLinked(item.id)"
            class="text-green-600"
        >
            {{ $t("itemAlreadyLinked") }}
        </span>
        <a
            v-else
            class="button w-full"
            @click="doLink()"
        >
            {{ $t("linkItem") }}
        </a>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import { mapState, mapMutations, mapGetters, mapActions } from "vuex"
import { initialDataPromise } from "@js/bootstrap"
import { enrichLightItem } from "@js/items/itemsUtils"
import PilotMixin from "@components/PilotMixin"
import ResponsiveMixin from "@components/ResponsiveMixin"

import ItemState from "../ItemState.vue"
import ItemStateDropdown from "../ItemStateDropdown.vue"
import ItemTypeIcon from "@views/itemTypes/ItemTypeIcon"
import ItemListActions from "./ItemListActions"

export default {
    name: "ItemListElement",
    mixins: [PilotMixin, ResponsiveMixin],
    components: {
        ItemState,
        ItemStateDropdown,
        ItemTypeIcon,
        ItemListActions,
    },
    props: {
        item: {
            type: Object,
            required: true,
        },
        // Can be "trash", "shared', "project", "channel", "dashboard", "picker", or a tab name from the main item list
        context: String,
    },
    data: () => ({
        isLoadingLink: false,
    }),
    computed: {
        ...mapState("itemTypes", ["itemTypes"]),
        ...mapState("bulk", ["bulkActionSelection", "wholeListSelected"]),
        ...mapGetters("itemDetail", ["isItemLinked"]),
        ...mapGetters("choices", ["getChoiceDisplay"]),
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
            return (
                this.context != "picker" &&
                this.context != "trash" &&
                this.context != "shared" &&
                this.item.user_has_access
            )
        },
        isSelectedForBulkAction() {
            return (
                (this.bulkActionSelection && this.bulkActionSelection[this.item.id]) ||
                this.wholeListSelected
            )
        },
        inactiveMentionGroups() {
            return {
                owners: !this.item.has_owners,
                channelOwners:
                    !this.item.channels ||
                    !_.some(this.item.channels.map((channel) => channel.has_owners)),
            }
        },
        channelNames() {
            return this.item.channels.map((channel) => channel.name).join(", ")
        },
        languageCode() {
            if (this.item.language) {
                return this.item.language.slice(0, 2).toUpperCase()
            }
        },
    },
    methods: {
        ...mapActions("itemDetail", ["linkItem"]),
        ...mapMutations("bulk", ["toggleForBulkAction", "setSingleObjectSelection"]),
        ...mapActions("itemActions", [
            "updateItemPublicationDate",
            "showItemPreviewModal",
            "bulkTrashItems",
            "bulkCopyItems",
        ]),

        onPublicationDateInput(publicationDate) {
            this.updateItemPublicationDate({
                id: this.item.id,
                publication_dt: publicationDate,
            })
        },
        doLink() {
            this.isLoadingLink = true
            this.linkItem(this.item)
                .then(() => {
                    this.isLoadingLink = false
                })
                .catch(() => {
                    this.isLoadingLink = false
                })
        },
    },
    watch: {
        item() {
            enrichLightItem(this.item)
        },
    },
    created() {
        initialDataPromise.then(() => {
            enrichLightItem(this.item)
        })
    },
    i18n: {
        messages: {
            fr: {
                explainItemAddedOnTop:
                    "Les contenus nouvellement créés apparaissent toujours en haut de la liste, sans prendre en compte les filtres ni le tri",
                itemAlreadyLinked: "Liaison ok !",
                itemLockedAndYouCanAccess:
                    "Ce contenu a été marqué comme privé par son auteur mais vous avez la permission d'y accéder",
                itemLockedAndYouHaveNoAccess:
                    "Ce contenu a été marqué comme privé par son auteur et vous ne pourrez l'afficher",
                linkItem: "Lier ce contenu",
                noChannelLinked: "Aucun canal associé",
                noProjectLinked: "Aucun projet associé",
                seeContent: "Contenu",
                clickToSetPublicationDate: "Cliquez pour choisir une date",
                thisItemHasNoLanguageSet: "Le contenu n'a pas de langue définie",
                itemLanguage: "Langue du contenu",
            },
            en: {
                explainItemAddedOnTop:
                    "Newly created contents always appears at the top of the list, ignoring the filters and ordering",
                itemAlreadyLinked: "Item already linked",
                itemLockedAndYouCanAccess:
                    "This content has been marked as private by its author but you have permission to access it",
                itemLockedAndYouHaveNoAccess:
                    "This content has been marked as private by its author and you will not be able to view it",
                linkItem: "Link content",
                noChannelLinked: "None",
                noProjectLinked: "None",
                seeContent: "Content",
                clickToSetPublicationDate: "Click to choose a publication date",
                thisItemHasNoLanguageSet: "The content does not have a defined language",
                itemLanguage: "Language of content",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/include_media.scss";
@import "~@sass/colors.scss";

.ItemListElement {
    @apply flex bg-white border border-gray-200 border-b-0;
    @apply flex-row items-center justify-between;
    min-height: 2.7rem;
    width: 100%;

    &:hover {
        background-color: #fafafa;
    }

    &:last-child {
        @apply border-b;
    }

    // Column mode for mobiles
    @include media("<=tablet") {
        @apply rounded-sm border border-gray-200 rounded;
        &:hover {
            @apply bg-white;
        }
    }
}
</style>
