<template>
<div class="AssetListContainer">
    <DropZone
        v-if="!usageLimitReached('asset_storage')"
        ref="dropzone"
        clickable=".startUpload"
        :previewTemplate="previewTemplate"
        @vdropzone-file-added="dropzoneFilesCount++"
        @vdropzone-removed-file="dropzoneFilesCount--"
        @vdropzone-success="onUploadSuccess"
        @vdropzone-total-upload-progress="onTotalUploadProgress"
    >
        <template #beforeDropzonePreview>
            <BigFilter
                :apiSource="apiSource"
                filterSchemaUrl="/api/big_filter/schema/assets/list/"
                :placeholder="$t('assetBigFilterPlaceholder')"
            />

            <div
                v-show="assets.length > 0 && !loadingInProgress.fetchAssetList"
                class="flex justify-between w-full items-end"
            >
                <div class="flex flex-wrap flex-grow items-center mr-8">
                    <div
                        class="button is-small is-white"
                        @click="$modal.show('createFolder')"
                    >
                        +{{ $t("createFolder") }}
                    </div>
                    <Label
                        v-for="folderLabel in labels.asset_folder"
                        class="ml-2 cursor-pointer"
                        :key="folderLabel.id"
                        :label="folderLabel"
                        @click.native="filterOnFolder(folderLabel)"
                    />
                </div>

                <div class="flex-shrink-0 flex items-end">
                    <OrderingSelector
                        defaultOrdering=""
                        :orderings="orderings"
                        :value="apiSource.ordering"
                        @orderingChange="apiSource.setOrdering"
                    />

                    <Pagination
                        class="ml-2"
                        :pagination="pagination"
                        @pageChange="apiSource.setPage"
                    />
                </div>
            </div>
        </template>

        <template #afterDropzonePreview>
            <Loadarium name="fetchAssetList" />

            <!-- We cannot use the Loadarium slot because <Dropzone> needs to see .startUpload elements -->
            <div
                v-show="!loadingInProgress.fetchAssetList"
                class="w-full my-5"
            >
                <!-- We can't use v-if because <Dropzone> must find .startUpload at init -->
                <div
                    class="startUpload AssetElement dropzone-bordered border-dashed border-2 p-4"
                    :class="{ hidden: !hasAnyAsset }"
                    key="uploadElement"
                >
                    <p class="text-gray-600 whitespace-no-wrap">
                        <Icon
                            class="mx-auto h-10 w-10 text-gray-400"
                            name="PlusCircle"
                        />
                        <a class="font-medium indigo-link">
                            {{ $t("addFiles") }}
                        </a>
                        {{ $t("orDragAndDrop") }}
                    </p>
                </div>

                <AssetListElement
                    v-for="asset in assets"
                    :asset="asset"
                    :context="context"
                    :isAssetLinked="isAssetLinked"
                    :key="asset.id"
                    @link="$emit('link', $event)"
                />

                <!-- We can't use v-if because <Dropzone> must find .startUpload at init -->
                <div v-show="!hasAnyAsset && !loadingInProgress.fetchAssetList">
                    <div
                        v-show="apiSource.hasFilter"
                        class="text-gray-800 font-bold text-center p-10 bg-gray-50 rounded"
                    >
                        {{ $t("noResults") }}
                    </div>
                    <AssetHelpText v-show="!apiSource.hasFilter" />
                </div>
            </div>

            <div
                v-show="assets.length > 0 && !loadingInProgress.fetchAssetList"
                class="flex flex-grow justify-end"
            >
                <Pagination
                    :pagination="pagination"
                    @pageChange="apiSource.setPage"
                />
            </div>
        </template>
    </DropZone>

    <Modal
        name="createFolder"
        height="auto"
        :pivotY="0.1"
    >
        <div class="p-8">
            {{ $t("name") }}:

            <CharInputWrapping
                :schema="{ placeholder: $t('name') }"
                v-model.trim="createdFolderName"
            />
            <div class="mt-4">
                <SmartButtonSpinner
                    class="is-blue"
                    name="createLabel"
                    @click="createFolder"
                >
                    {{ $t("ok") }}
                </SmartButtonSpinner>
                <button
                    class="button"
                    type="button"
                    @click="$modal.hide('createFolder')"
                >
                    {{ $t("cancel") }}
                </button>
            </div>
        </div>
    </Modal>
</div>
</template>

<script>
import _ from "lodash"
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import { DZ_PREVIEW_TEMPLATE_WITHOUT_IMAGE } from "@js/dropzoneTemplates"
import PilotMixin from "@components/PilotMixin"
import AssetConverter from "@js/AssetConverter"

import UsageLimitAlert from "@components/UsageLimitAlert.vue"
import DropZone from "@components/DropZone"

import BigFilter from "@views/bigFilter/BigFilter"
import OrderingSelector from "@views/bigFilter/OrderingSelector"
import Pagination from "@components/Pagination"
import AssetListElement from "./AssetListElement"
import AssetHelpText from "./AssetHelpText"
import Label from "@views/labels/Label.vue"
import { DEFAULT_LABEL_BG_COLOR, DEFAULT_LABEL_COLOR } from "@/store/modules/LabelStore"
import CharInputWrapping from "@components/forms/widgets/CharInputWrapping"

export default {
    name: "AssetList",
    mixins: [PilotMixin],
    components: {
        UsageLimitAlert,
        DropZone,

        BigFilter,
        OrderingSelector,
        Pagination,
        AssetListElement,
        AssetHelpText,
        Label,
        CharInputWrapping,
    },
    props: {
        // Can be "list" or "picker"
        context: {
            type: String,
            default: "list",
        },
        isAssetLinked: {
            type: Function,
            default: () => false,
        },
    },
    data: () => ({
        previewTemplate: DZ_PREVIEW_TEMPLATE_WITHOUT_IMAGE,
        assetConverter: new AssetConverter(),
        createdFolderName: "",
        dropzoneFilesCount: 0,
    }),
    computed: {
        ...mapState("labels", ["labels"]),
        ...mapState("assetList", ["pagination", "assets", "apiSource"]),
        ...mapGetters("usageLimits", ["usageLimitReached"]),
        ...mapState("loading", ["loadingInProgress"]),
        orderings() {
            return [
                { value: "", label: this.$t("sortByDefault") },
                { value: "title", label: this.$t("sortByTitle") },
                { value: "filetype", label: this.$t("sortByFileType") },
                { value: "-created_at", label: this.$t("sortByCreationDateNewestFirst") },
            ]
        },
        hasAnyAsset() {
            return this.assets.length > 0 || this.dropzoneFilesCount
        },
    },
    methods: {
        ...mapActions("labels", ["fetchLabels", "createLabel"]),
        ...mapActions("assetList", ["fetchAssetList", "addUploadedAsset"]),
        onUploadSuccess(file) {
            this.addUploadedAsset(file).then(() => {
                if (this.$refs.dropzone) {
                    this.$refs.dropzone.removeFile(file)
                }
            })
        },
        onTotalUploadProgress(uploadProgress) {
            this.assetConverter.onTotalUploadProgress(uploadProgress)
        },
        filterOnFolder(folderLabel) {
            let query = _.clone(this.apiSource.query)
            delete query.page
            query.folder = folderLabel.id
            this.apiSource.setQuery(query)
        },
        createFolder() {
            this.createLabel({
                name: this.createdFolderName,
                target_type: "asset_folder",
                order: this.labels.asset_folder.length,
                color: DEFAULT_LABEL_COLOR,
                background_color: DEFAULT_LABEL_BG_COLOR,
            }).then((label) => {
                this.createdFolderName = ""
                this.$modal.hide("createFolder")
            })
        },
    },
    watch: {
        "apiSource.url"() {
            this.fetchAssetList()
        },
    },
    created() {
        this.fetchAssetList()
        this.fetchLabels("asset_folder")
    },
    i18n: {
        messages: {
            fr: {
                assetBigFilterPlaceholder: "Rechercher dans les medias",
                createFolder: "Créer un dossier",
                dragHereToUpload: "Glissez-déposez des fichiers ou",
                sortByDefault: "Défaut",
                sortByTitle: "Titre",
                sortByFileType: "Type de fichier",
                sortByCreationDateNewestFirst: "Date de création",
                browse: "sélectionnez les",
            },
            en: {
                assetBigFilterPlaceholder: "Search the assets",
                createFolder: "Create a folder",
                dragHereToUpload: "Drag&drop files here or",
                sortByDefault: "Default",
                sortByTitle: "Title",
                sortByFileType: "File type",
                sortByCreationDateNewestFirst: "Creation date",
                browse: "browse",
            },
        },
    },
}
</script>
