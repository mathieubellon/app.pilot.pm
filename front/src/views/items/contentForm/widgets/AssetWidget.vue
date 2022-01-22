<template>
<div class="AssetWidget">
    <div v-if="isAssemblyError">
        {{ $t("assemblyError") }}

        <button
            class="button primary AssetWidget__action"
            @click="retryConversion()"
        >
            {{ $t("tryAgain") }}
        </button>
    </div>
    <div v-else-if="assetConverter.getConversionStatusAborted">
        {{ $t("conversionStatusPollingAborted") }}

        <button
            class="button primary AssetWidget__action"
            @click="assetConverter.waitForAssetConversionStatus(asset)"
        >
            {{ $t("tryAgain") }}
        </button>
    </div>
    <div v-else-if="isAssemblyRunning">
        <Spinner />
        {{ $t("assemblyExecuting") }}
    </div>

    <div
        v-if="asset"
        key="updateFile"
    >
        <div
            v-show="
                !isAssemblyError && !assetConverter.getConversionStatusAborted && !isAssemblyRunning
            "
        >
            <DropZone
                ref="dropzoneUpdate"
                :assetId="asset.id"
                clickable=".startUpload"
                :maxNumberOfFiles="1"
                :previewTemplate="previewTemplate"
                @vdropzone-file-added="onFileAdded"
                @vdropzone-success="onFileUpdateSuccess"
                @vdropzone-total-upload-progress="onTotalUploadProgress"
            >
                <div
                    v-show="!isUploadingFile"
                    class="w-full"
                    slot="afterDropzonePreview"
                >
                    <div v-if="hasWorkingImages">
                        <div v-for="(workingImageUrl, index) in asset.working_urls">
                            <AnnotatableImage
                                :annotations="annotations"
                                :annotationsKey="`${schema.name}-${index}`"
                                :src="workingImageUrl"
                                @annotations="onAnnotations"
                            />
                            <br v-if="index < asset.working_urls.length - 1" />
                        </div>
                    </div>

                    <AssetPreview
                        v-else
                        :asset="value"
                        context="itemMedia"
                    />

                    <div class="w-full text-center font-bold">{{ asset.name }}</div>
                    <div
                        v-if="value.in_media_library"
                        class="w-full text-center text-indigo-600"
                    >
                        <Icon
                            name="Asset"
                            size="20px"
                        />
                        {{ $t("addedFromMediaLibrary") }}
                    </div>

                    <div class="startUpload dropzone-bordered w-full mt-2 p-3">
                        <div class="text-center">
                            <Icon
                                class="text-gray-400 -mt-1"
                                name="Upload"
                            />
                            <div class="mt-1 text-sm text-gray-600 whitespace-no-wrap">
                                <div class="mb-2">{{ $t("dragHereToUpload") }}</div>
                                <div>
                                    <a
                                        class="button is-indigo is-small px-1"
                                        type="button"
                                    >
                                        {{ $t("linkAssetFromComputer") }}
                                    </a>
                                    {{ $t("or") }}
                                    <a
                                        class="button is-indigo is-small mt-1 px-1"
                                        @click.stop="openOffPanel(`assetsField-${schema.name}`)"
                                    >
                                        {{ $t("linkAssetFromLibrary") }}
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>

                    <a
                        class="button is-small is-blue w-full mt-2"
                        :href="asset.file_url"
                    >
                        <Icon
                            class="text-white"
                            name="Download"
                        />
                        <span>
                            {{ $t("downloadOriginal", { size: humanFileSize(asset.size) }) }}
                        </span>
                    </a>

                    <Deletarium
                        deleteButtonClass="button is-small is-text mt-2 w-full"
                        :deleteButtonText="$t('deleteFile')"
                        loadingName="deleteAsset"
                        @delete="onFileDeleted"
                    />
                </div>
            </DropZone>
        </div>
    </div>

    <div
        v-else
        key="addFile"
    >
        <DropZone
            class="dropzone-bordered"
            :previewTemplate="previewTemplate"
            @vdropzone-file-added="onFileAdded"
            @vdropzone-success="onFileCreateSuccess"
            @vdropzone-total-upload-progress="onTotalUploadProgress"
        >
            <template #dropzoneMessage>
                <div class="text-center">
                    <Icon
                        class="mx-auto h-10 w-10 text-gray-400"
                        name="File"
                    />
                    <div class="mt-1 text-sm text-gray-600 whitespace-no-wrap">
                        <div class="mb-2">{{ $t("dragHereToUpload") }}</div>
                        <div>
                            <a
                                class="button is-indigo is-small px-1"
                                type="button"
                            >
                                {{ $t("linkAssetFromComputer") }}
                            </a>
                            {{ $t("or") }}
                            <a
                                class="button is-indigo is-small mt-1 px-1"
                                @click.stop="openOffPanel(`assetsField-${schema.name}`)"
                            >
                                {{ $t("linkAssetFromLibrary") }}
                            </a>
                        </div>
                    </div>
                </div>
            </template>
        </DropZone>
    </div>

    <OffPanel
        :name="`assetsField-${schema.name}`"
        position="left"
        width="75%"
    >
        <div slot="offPanelTitle">{{ $t("searchInMediaLibrary") }}</div>
        <div slot="offPanelBody">
            <AssetList
                context="picker"
                @link="onAssetSelectedFromLibrary"
            />
        </div>
    </OffPanel>
</div>
</template>

<script>
import _ from "lodash"
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import urls from "@js/urls.js"
import { $httpX } from "@js/ajax.js"
import { humanFileSize } from "@js/localize.js"
import { getFileProperties } from "@js/assetsUtils.js"
import { DZ_PREVIEW_TEMPLATE_WITHOUT_IMAGE } from "@js/dropzoneTemplates"
import { getInMemoryApiSource } from "@js/apiSource"
import PilotMixin from "@components/PilotMixin"

import DropZone from "@components/DropZone.vue"
import AnnotatableImage from "../annotations/image/AnnotatableImage.vue"

import AssetPreview from "@views/assets/AssetPreview.vue"
import AssetList from "@views/assets/list/AssetList.vue"
import AssetConverter from "@js/AssetConverter"

export default {
    name: "AssetWidget",
    mixins: [PilotMixin],
    components: {
        DropZone,
        AnnotatableImage,

        AssetPreview,
        AssetList,
    },
    props: ["schema", "value", "annotations"],
    data: () => ({
        // Clone to prevent memory leak incurred by a top-level reactive object.
        djangoSettings: _.cloneDeep(window.pilot.djangoSettings),
        urls: urls,
        previewTemplate: DZ_PREVIEW_TEMPLATE_WITHOUT_IMAGE,
        pendingAsset: null,
        isUploadingFile: false,
        isAssemblyRunning: false,
        isAssemblyError: false,
        assetConverter: new AssetConverter(),
        humanFileSize,
    }),
    computed: {
        // Alias, to be explicit in code
        asset() {
            return this.value
        },
        offPanelName() {
            return "assetsLibraryFor" + this.schema.name
        },
        hasWorkingImages() {
            return (
                this.asset &&
                (this.asset.filetype === "image" || this.asset.filetype === "pdf") &&
                this.asset.working_urls &&
                this.asset.working_urls.length > 0
            )
        },
    },
    methods: {
        ...mapMutations("assetList", ["setApiSource"]),
        onFileAdded() {
            this.isUploadingFile = true
            this.isAssemblyRunning = false
            this.isAssemblyError = false
        },
        onFileDeleted() {
            this.$emit("input", null)
        },
        onFileCreateSuccess(file) {
            let assetData = getFileProperties(file)
            _.assign(assetData, {
                assetId: file.assetId, // Temporary creation by AssetId
                in_media_library: false,
            })

            $httpX({
                name: "addUploadedAsset",
                commit: this.$store.commit,
                url: urls.assets,
                method: "POST",
                data: assetData,
            }).then((response) => {
                this.pendingAsset = response.data
                // Updating the asset will start a new transloadit conversion.
                // We can start polling it now.
                this.isAssemblyRunning = true
                this.assetConverter.waitForAssetConversionStatus(this.pendingAsset)
                file.previewElement.outerHTML = ""
                this.isUploadingFile = false
            })
        },
        onFileUpdateSuccess(file) {
            let assetData = getFileProperties(file)
            assetData.fileChanged = true

            $httpX({
                name: "updateAssetDetail",
                commit: this.$store.commit,
                url: urls.assets.format({ id: this.asset.id }),
                method: "PATCH",
                data: assetData,
            }).then((response) => {
                this.pendingAsset = response.data
                // Updating the asset will start a new transloadit conversion.
                // We can start polling it now.
                this.isAssemblyRunning = true
                this.assetConverter.waitForAssetConversionStatus(this.pendingAsset)
                file.previewElement.outerHTML = ""
                this.isUploadingFile = false
            })
        },
        retryConversion() {
            this.isAssemblyError = false
            this.assetConverter.startConversion(this.pendingAsset)
        },
        onConversionStatusUpdate(asset) {
            if (asset.is_assembly_completed) {
                this.isAssemblyRunning = false
                this.pendingAsset = null
                this.$emit("input", asset)
            } else if (asset.is_assembly_error) {
                this.isAssemblyRunning = false
                this.isAssemblyError = true
            }
        },
        onAnnotations(annotationsData) {
            this.$emit("annotations", annotationsData)
        },
        onTotalUploadProgress(uploadProgress) {
            this.assetConverter.onTotalUploadProgress(uploadProgress)
        },
        onAssetSelectedFromLibrary(asset) {
            this.$emit("input", asset)
            this.closeOffPanel(`assetsField-${this.schema.name}`)
        },
    },
    created() {
        this.assetConverter.on("conversionStatusUpdate", this.onConversionStatusUpdate)
        this.setApiSource(getInMemoryApiSource(urls.assetsLibrary))
    },
    i18n: {
        messages: {
            fr: {
                addedFromMediaLibrary: "Ce fichier provient de la médiathèque.",
                assemblyExecuting:
                    "Traitement du fichier en cours, veuillez attendre la fin de l'opération. Le contenu sera alors sauvegardé automatiquement.",
                conversionStatusPollingAborted:
                    "Le traitement du fichier prends beaucoup de temps.",
                deleteFile: "Supprimer le fichier",
                downloadOriginal: "Télécharger l'original ({size})",
                dragHereToUpload: "Glissez-déposez un fichier ou sélectionnez le",
                tryAgain: "Essayer à nouveau",
                seeAssetDetails: "Voir les détails du fichier",
                updateFile: "Mettre à jour le fichier",
            },
            en: {
                addedFromMediaLibrary: "This file comes from the media library.",
                assemblyExecuting:
                    "File processing in progress, please wait until completion. The content will then be saved automatically.",
                conversionStatusPollingAborted: "The file processing seems quite long.",
                deleteFile: "Delete file",
                downloadOriginal: "Download the original ({size})",
                dragHereToUpload: "Drag&drop a file or select it",
                tryAgain: "Try again",
                seeAssetDetail: "See file details",
                updateFile: "Update the file",
            },
        },
    },
}
</script>

<style lang="scss">
.AssetWidget .AssetPreview {
    text-align: center; /* align center all inline elements */

    img {
        display: inline-block;
        line-height: 0;
        max-width: 100%;
        width: 100%; // For IE11
        transition: box-shadow 200ms ease-out;
        border-radius: 0;

        height: auto;
        -ms-interpolation-mode: bicubic;
        vertical-align: middle;
    }
}
.AssetWidget__action {
    margin-bottom: 1em;
}
</style>
