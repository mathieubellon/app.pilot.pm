<template>
<div class="ItemDrawer DrawerTranslations">
    <div v-if="isMasterPreviewVisible">
        <div class="p-5 flex items-center content-center justify-center">
            <a @click="hideMasterPreview">{{ $t("hidePreview") }}</a>
        </div>

        <Loadarium name="fetchMasterTranslationPreview">
            <ItemContentReadOnly :itemReadOnly="masterTranslationPreview" />
        </Loadarium>
    </div>

    <template v-else>
        <div class="ItemDrawer__Header">
            {{ $t("translations") }}

            <div
                class="ItemDrawer__Header__Close"
                @click="closePanel()"
            >
                {{ $t("close") }}
            </div>
        </div>

        <!--Languages-->
        <div class="text-sm font-semibold mb-2">{{ $t("currentLanguage") }}</div>
        <Popper
            v-if="currentDesk.itemLanguagesEnabled"
            closeOnClickSelector=".willClose"
            triggerElementName="PopperRef"
            triggerType="click"
        >
            <template #triggerElement>
                <button
                    class="button"
                    ref="PopperRef"
                >
                    <BarLoader v-if="fieldsCurrentlyUpdating.language" />
                    <template v-else>
                        <Icon
                            class="mr-1 text-gray-500"
                            name="Language"
                            size="20px"
                        />
                        <template v-if="item.language">
                            {{ getChoiceDisplay("languagesChoices", item.language) }}
                        </template>
                        <template v-else>{{ $t("noLanguage") }}</template>
                        <!-- The empty span is required to correctly align with flex display -->
                        <span>
                            <Icon
                                class="caret"
                                name="ChevronDown"
                            />
                        </span>
                    </template>
                </button>
            </template>

            <template #content>
                <button
                    v-for="languageChoice in choices.languages"
                    class="menu-item willClose"
                    @click="partialUpdateItem({ language: languageChoice.name })"
                >
                    {{ languageChoice.label }}
                </button>
            </template>
        </Popper>
        <div class="TranslationsTree mt-5">
            <div class="text-sm font-semibold mb-2">
                {{ labels.translations }}
            </div>
            <!--Sibling view-->
            <div v-if="item.master_translation">
                <Spinner v-if="fieldsCurrentlyUpdating.translations_id" />
                <div class="flex items-center justify-between mb-2">
                    <SmartLink
                        class="button is-small is-white flex-shrink flex-grow justify-start truncate"
                        :to="item.master_translation.url"
                    >
                        {{ item.master_translation.title }}
                    </SmartLink>
                    <div class="flex flex-shrink-0 flex-no-wrap items-center">
                        <a
                            class="mr-1 text-sm"
                            @click="showMasterPreview"
                        >
                            {{ $t("preview") }}
                        </a>
                        <span class="text-xs text-yellow-600 px-2 py-1 rounded bg-yellow-300">
                            <span class="text-sm text-gray-800 mr-2 font-semibold">master</span>
                            <template v-if="item.master_translation.language">
                                {{ item.master_translation.language }}
                            </template>
                        </span>
                    </div>
                </div>
                <div
                    v-for="translationSibling in sortedTranslationSiblings"
                    class="flex items-center justify-between mb-1 w-full"
                    :class="{ 'bg-gray-100': translationSibling.id == item.id }"
                >
                    <div class="flex items-center flex-shrink flex-grow w-full truncate">
                        <SmartLink
                            class="button is-small"
                            :class="{
                                late: translationSibling.updated_at > item.updated_at,
                                'is-white': translationSibling.id != item.id,
                            }"
                            :to="translationSibling.url"
                        >
                            <Icon
                                name="ChevronRight"
                                size="12px"
                            />
                            {{ translationSibling.title }}
                        </SmartLink>
                    </div>
                    <div class="flex items-center flex-shrink-0">
                        <div
                            v-if="translationSibling.language"
                            class="text-xs font-bold text-yellow-600 px-2 py-1 rounded bg-yellow-300 content-end"
                        >
                            {{ translationSibling.language }}
                        </div>
                        <a
                            class="button is-xsmall is-white"
                            @click="unlinkItem(translationItem)"
                        >
                            <Icon name="Close" />
                        </a>
                    </div>
                </div>
            </div>
            <!--Master view-->
            <div
                v-else
                class="w-full"
            >
                <Spinner v-if="fieldsCurrentlyUpdating.translations_id" />
                <div class="flex items-center justify-between mb-2">
                    <div class="button is-small flex-shrink flex-grow justify-start truncate">
                        {{ item.title }}
                    </div>
                    <div
                        class="text-xs text-yellow-600 px-2 py-1 rounded flex-shrink-0 bg-yellow-300"
                    >
                        <span class="text-sm text-gray-800 mr-2 font-semibold">master</span>
                        {{ getChoiceDisplay("languagesChoices", item.language) }}
                    </div>
                </div>
                <div
                    v-for="translationItem in sortedTranslations"
                    class="flex items-center justify-between mb-1 w-full"
                >
                    <div class="flex items-center flex-shrink flex-grow w-full truncate">
                        <SmartLink
                            class="button is-small is-white"
                            :class="{ late: translationItem.updated_at > item.updated_at }"
                            :to="translationItem.url"
                        >
                            <Icon
                                name="ChevronRight"
                                size="12px"
                            />
                            {{ translationItem.title }}
                        </SmartLink>
                    </div>
                    <div class="flex items-center flex-shrink-0">
                        <div
                            v-if="translationItem.language"
                            class="text-xs text-yellow-600 px-2 py-1 rounded bg-yellow-300 content-end"
                        >
                            {{ translationItem.language }}
                        </div>
                        <a
                            class="button is-xsmall is-white"
                            @click="unlinkItem(translationItem)"
                        >
                            <Icon name="Close" />
                        </a>
                    </div>
                </div>

                <div class="flex justify-between w-full mt-4">
                    <a
                        class="text-sm ml-5"
                        @click.prevent="openOffPanel('createTranslation')"
                    >
                        ＋{{ $t("createTranslation") }}
                    </a>
                    <a
                        class="text-sm"
                        @click.prevent="openOffPanel('translationsPicker')"
                    >
                        {{ $t("selectTranslation") }}
                    </a>
                </div>
            </div>
        </div>
    </template>

    <OffPanel
        name="createTranslation"
        :stretched="true"
    >
        <div slot="offPanelTitle">{{ $t("createTranslationFor") }} "{{ item.title }}"</div>

        <template slot="offPanelBody">
            <ItemAddForm
                :initialItemData="initialTranslationData"
                :isTranslation="true"
                :itemType="item.item_type"
                @saved="onTranslationCreated"
            />
            <UsageLimitAlert usageLimitName="items" />
        </template>
    </OffPanel>

    <OffPanel
        name="translationsPicker"
        :title="$t('selectTranslation')"
        width="70%"
    >
        <ItemPicker slot="offPanelBody" />
    </OffPanel>
</div>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { sortByAlphaString } from "@js/utils.js"
import PilotMixin from "@components/PilotMixin"

import ItemPicker from "@components/picker/ItemPicker.vue"
import Label from "@views/labels/Label.vue"
import LabelSelect from "@views/labels/LabelSelect.vue"
import UsageLimitAlert from "@components/UsageLimitAlert.vue"
import ItemAddForm from "@views/items/ItemAddForm.vue"
import ItemContentReadOnly from "@views/items/contentForm/ItemContentReadOnly"

export default {
    name: "DrawerTranslations",
    mixins: [PilotMixin],
    components: {
        ItemPicker,
        Label,
        LabelSelect,
        UsageLimitAlert,
        ItemAddForm,
        ItemContentReadOnly,
    },
    data: () => ({
        isMasterPreviewVisible: false,
    }),
    computed: {
        ...mapState("itemDetail", ["item", "fieldsCurrentlyUpdating", "masterTranslationPreview"]),
        ...mapState("choices", ["choices"]),
        ...mapGetters("choices", ["getChoiceDisplay"]),
        labels() {
            let labels = {
                translations: this.$t("translations"),
            }
            if (this.item.itemType) {
                _.forEach(this.item.itemType.metadata_schema, (schema, fieldName) => {
                    if (schema.label) {
                        labels[fieldName] = schema.label
                    }
                })
            }
            return labels
        },
        sortedTranslations() {
            return sortByAlphaString(this.item.translations, (item) => item.language)
        },
        sortedTranslationSiblings() {
            return sortByAlphaString(this.item.translation_siblings, (item) => item.language)
        },
        initialTranslationData() {
            return _.defaults({}, _.omit(this.item, ["id", "language"]))
        },
    },
    methods: {
        ...mapActions("itemDetail", [
            "partialUpdateItem",
            "linkItem",
            "unlinkItem",
            "closePanel",
            "fetchMasterTranslationPreview",
        ]),
        onTranslationCreated(item) {
            this.linkItem(item)
            this.closeOffPanel("createTranslation")
        },
        showMasterPreview() {
            this.fetchMasterTranslationPreview()
            this.isMasterPreviewVisible = true
        },
        hideMasterPreview() {
            this.isMasterPreviewVisible = false
        },
    },
    i18n: {
        messages: {
            fr: {
                createTranslation: "Créer une traduction",
                createTranslationFor: "Nouvelle traduction pour",
                currentLanguage: "Langue du contenu",
                hidePreview: "Fermer l'aperçu",
                selectTranslation: "Ajouter des traductions existantes",
                translations: "Traductions",
            },
            en: {
                createTranslation: "Create a translation",
                createTranslationFor: "New translation for",
                currentLanguage: "Content language",
                hidePreview: "Close preview",
                selectTranslation: "Add existing translation",
                translations: "Translations",
            },
        },
    },
}
</script>
