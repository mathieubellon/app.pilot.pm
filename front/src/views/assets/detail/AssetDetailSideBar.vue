<template>
<div class="AssetDetailSideBar">
    <transition
        enter-active-class="animated fadeIn"
        leave-active-class="animated fadeOut"
        mode="out-in"
    >
        <div
            v-if="!asset.id || isUploadingFile"
            class="bg-white border border-gray-200 rounded px-3 py-5"
        >
            <BarLoader
                :color="colors.grey500"
                :width="100"
                widthUnit="%"
            />
        </div>

        <div v-else>
            <div class="AssetDetailSideBar__panel">
                <div class="AssetDetailSideBar__panelHeader">
                    <div class="AssetDetailSideBar__panelTitle">{{ $t("assetFolder") }}</div>
                    <LabelSelect
                        :multiple="false"
                        placement="right"
                        targetType="asset_folder"
                        triggerElementName="PopperRef"
                        :value="asset.folder"
                        @input="onFolderInput"
                    >
                        <template #triggerElement>
                            <a
                                class="AssetDetailSideBar__panelHeaderLink button is-small"
                                ref="PopperRef"
                            >
                                {{ $t("edit") }}
                            </a>
                        </template>
                    </LabelSelect>
                </div>

                <Label
                    v-if="asset.folder"
                    class="text-lg w-full"
                    :goToListOnClick="true"
                    :label="asset.folder"
                />
                <div v-else>{{ $t("noFolder") }}</div>
            </div>

            <div
                v-if="asset.filetype == 'image'"
                class="AssetDetailSideBar__panel"
            >
                <div class="AssetDetailSideBar__panelHeader">
                    <div class="AssetDetailSideBar__panelTitle">{{ $t("html.attributes") }}</div>
                    <a
                        class="AssetDetailSideBar__panelHeaderLink button is-small"
                        @click="$refs.editHtmlAttributes.openFormPanel(asset)"
                    >
                        {{ $t("edit") }}
                    </a>
                </div>

                <table>
                    <tr>
                        <td class="text-sm font-medium text-gray-700">{{ $t("html.caption") }}</td>
                        <td class="pl-3">{{ asset.html_caption | defaultVal("∅") }}</td>
                    </tr>
                    <tr>
                        <td class="text-sm font-medium text-gray-700">{{ $t("html.title") }}</td>
                        <td class="pl-3">{{ asset.html_title | defaultVal("∅") }}</td>
                    </tr>
                    <tr>
                        <td class="text-sm font-medium text-gray-700">{{ $t("html.altText") }}</td>
                        <td class="pl-3">{{ asset.html_alt | defaultVal("∅") }}</td>
                    </tr>
                </table>
            </div>

            <div class="AssetDetailSideBar__panel">
                <div class="AssetDetailSideBar__panelHeader">
                    <div class="AssetDetailSideBar__panelTitle">{{ $t("extension") }}</div>
                </div>

                {{ asset.extension }}
            </div>

            <div class="AssetDetailSideBar__panel">
                <div class="AssetDetailSideBar__panelHeader">
                    <div class="AssetDetailSideBar__panelTitle">{{ $t("weight") }}</div>
                </div>

                {{ asset.readable_file_size }}
            </div>

            <div
                v-if="asset.height || asset.widht"
                class="AssetDetailSideBar__panel"
            >
                <div class="AssetDetailSideBar__panelHeader">
                    <div class="AssetDetailSideBar__panelTitle">{{ $t("size") }}</div>
                </div>

                <table>
                    <tr>
                        <td class="text-sm font-medium text-gray-700">{{ $t("width") }}</td>
                        <td class="pl-3">{{ asset.width }}px</td>
                    </tr>
                    <tr>
                        <td class="text-sm font-medium text-gray-700">{{ $t("height") }}</td>
                        <td class="pl-3">{{ asset.height }}px</td>
                    </tr>
                </table>
            </div>

            <div class="AssetDetailSideBar__panel">
                <div class="AssetDetailSideBar__panelHeader">
                    <div class="AssetDetailSideBar__panelTitle">{{ $t("linkedToItems") }}</div>
                </div>

                <div v-if="!asset.items || asset.items.length == 0">
                    {{ $t("noLinkedItemsYet") }}
                </div>
                <template
                    v-else
                    v-for="item in asset.items"
                >
                    <SmartLink :to="item.url">[{{ item.id }}] {{ item.title }}</SmartLink>
                </template>
            </div>

            <div class="AssetDetailSideBar__panel">
                <div class="AssetDetailSideBar__panelHeader">
                    <div class="AssetDetailSideBar__panelTitle">{{ $t("linkedToProjects") }}</div>
                </div>

                <div v-if="!asset.projects || asset.projects.length == 0">
                    {{ $t("noLinkedProjectsYet") }}
                </div>
                <template
                    v-else
                    v-for="project in asset.projects"
                >
                    <SmartLink :to="project.url">[{{ project.id }}] {{ project.name }}</SmartLink>
                </template>
            </div>

            <div class="AssetDetailSideBar__panel">
                <div class="AssetDetailSideBar__panelHeader">
                    <div class="AssetDetailSideBar__panelTitle">{{ $t("linkedToChannels") }}</div>
                </div>

                <div v-if="!asset.channels || asset.channels.length == 0">
                    {{ $t("noLinkedChannelsYet") }}
                </div>
                <template
                    v-else
                    v-for="channel in asset.channels"
                >
                    <SmartLink :to="channel.url">[{{ channel.id }}] {{ channel.name }}</SmartLink>
                </template>
            </div>

            <div class="AssetDetailSideBar__panel">
                <div class="AssetDetailSideBar__panelHeader">
                    <div class="AssetDetailSideBar__panelTitle">{{ $t("informations") }}</div>
                </div>

                <table>
                    <tr>
                        <td class="text-sm font-medium text-gray-700">{{ $t("createdBy") }}</td>
                        <td class="pl-3">
                            <UserDisplay
                                v-if="asset.created_by"
                                :user="asset.created_by"
                            />
                            <template v-else>-</template>
                        </td>
                    </tr>
                    <tr>
                        <td class="text-sm font-medium text-gray-700">{{ $t("updatedBy") }}</td>
                        <td class="pl-3">
                            <UserDisplay
                                v-if="asset.created_by"
                                :user="asset.created_by"
                            />
                            <template v-else>-</template>
                        </td>
                    </tr>
                </table>
            </div>
        </div>
    </transition>

    <AutoFormInPanel
        name="editHtmlAttributes"
        ref="editHtmlAttributes"
        :saveUrl="urls.assets"
        :schema="htmlAttributesFormSchema"
        :title="$t('html.attributes')"
        @updated="setAsset"
    />
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import Label from "@views/labels/Label.vue"
import LabelSelect from "@views/labels/LabelSelect.vue"
import { ToggleButton } from "vue-js-toggle-button"

export default {
    name: "AssetDetailSideBar",
    mixins: [PilotMixin],
    components: {
        Label,
        LabelSelect,
        ToggleButton,
    },
    computed: {
        ...mapState("assetDetail", ["asset", "isUploadingFile"]),
        ...mapGetters("users", ["myPermissions"]),
        htmlAttributesFormSchema() {
            return [
                {
                    name: "html_caption",
                    type: "char",
                    label: this.$t("html.caption"),
                    placeholder: this.$t("html.caption"),
                },
                {
                    name: "html_title",
                    type: "char",
                    label: this.$t("html.title"),
                    placeholder: this.$t("html.title"),
                },
                {
                    name: "html_alt",
                    type: "char",
                    label: this.$t("html.altText"),
                    placeholder: this.$t("html.altText"),
                },
            ]
        },
    },
    methods: {
        ...mapMutations("assetDetail", ["setAsset"]),
        ...mapActions("assetDetail", ["partialUpdateAsset"]),
        onFolderInput(folder) {
            this.partialUpdateAsset({
                folder_id: folder ? folder.id : null,
            })
        },
    },
    i18n: {
        messages: {
            fr: {
                extension: "Extension",
                height: "Hauteur",
                html: {
                    altText: "Texte alternatif",
                    attributes: "Attributs html",
                    caption: "Légende",
                    title: "Titre",
                },
                label: "Label",
                linkedToChannels: "Lié aux canaux",
                linkedToItems: "Lié aux contenus",
                linkedToProjects: "Lié aux projets",
                noFolder: "Aucun",
                noLabel: "Aucune",
                noLinkedChannelsYet: "Ce fichier n'est lié à aucun canal pour le moment",
                noLinkedItemsYet: "Ce fichier n'est lié à aucun contenu pour le moment",
                noLinkedProjectsYet: "Ce fichier n'est lié à aucun projet pour le moment",
                noOwners: "Aucun responsable",
                parentAsset: "Canal parent",
                selectParentAsset: "Sélectionner le canal parent",
                size: "Taille",
                weight: "Poids",
                width: "Largeur",
            },
            en: {
                extension: "Extension",
                height: "Height",
                html: {
                    altText: "Alternative text",
                    attributes: "Html attributes",
                    caption: "Caption",
                    title: "Title",
                },
                label: "Label",
                linkedToChannels: "Linked to channels",
                linkedToItems: "Linked to contents",
                linkedToProjects: "Linked to projects",
                noFolder: "None",
                noLabel: "None",
                noLinkedChannelsYet: "This asset is not linked to any channel at the moment",
                noLinkedItemsYet: "This asset is not linked to any content at the moment",
                noLinkedProjectsYet: "This asset is not linked to any project at the moment",
                noOwners: "No owner",
                parentAsset: "Parent asset",
                selectParentAsset: "Select parent asset",
                size: "Size",
                weight: "Weight",
                width: "Width",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.AssetDetailSideBar {
    @apply flex flex-col;
}

.AssetDetailSideBar__panel {
    @apply flex-col bg-white border border-gray-200 rounded p-3 mb-2;

    overflow: hidden;
    text-overflow: ellipsis;

    &:hover {
        .AssetDetailSideBar__panelHeaderLink {
            visibility: visible;
        }
    }
}

.AssetDetailSideBar__panelHeader {
    @apply mb-1 flex flex-grow justify-between items-center w-full;

    .AssetDetailSideBar__panelTitle {
        @apply text-sm font-bold text-gray-800;
    }
}

.AssetDetailSideBar__panelHeaderLink {
    visibility: hidden;
}
.AssetDetailSideBar__panelUserElement {
    @apply flex items-center justify-between bg-gray-50 p-1 mb-1 rounded;
}
</style>
