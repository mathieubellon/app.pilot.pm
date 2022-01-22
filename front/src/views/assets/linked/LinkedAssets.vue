<template>
<DropZone
    :class="{
        'items-start': !gridView,
    }"
    ref="dropzone"
    clickable=".startUpload"
    :language="{
        dictDefaultMessage: '',
        uploadSuccessMessage: $t('assemblyExecuting'),
    }"
    :previewTemplate="previewTemplate"
    @vdropzone-file-added="dropzoneFilesCount++"
    @vdropzone-removed-file="dropzoneFilesCount--"
    @vdropzone-success="onUploadSuccess"
    @vdropzone-total-upload-progress="onTotalUploadProgress"
>
    <template #beforeDropzonePreview>
        <UsageLimitAlert usageLimitName="asset_storage" />

        <Popper
            closeOnClickSelector=".willClose"
            :lazyLoading="false"
            triggerElementName="PopperRef"
        >
            <template #triggerElement>
                <button
                    class="button bg-gray-300"
                    ref="PopperRef"
                >
                    {{ $t("addOneOrMoreFiles") }}
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
                <a
                    v-if="!usageLimitReached('asset_storage')"
                    class="menu-item startUpload willClose"
                >
                    {{ $t("linkAssetFromComputer") }}
                </a>
                <a
                    class="menu-item willClose"
                    @click="openOffPanel('assetsLibrary')"
                >
                    {{ $t("linkAssetFromLibrary") }}
                </a>
                <a
                    class="menu-item willClose"
                    @click="showAssetUrlForm()"
                >
                    {{ $t("asExternalLink") }}
                </a>
                <hr class="my-1" />
                <a
                    v-if="zipStep == 'ready'"
                    class="menu-item"
                    :class="{ disabled: linkedAssets.length == 0 }"
                    @click="requestAssetsZip()"
                >
                    {{ $t("downloadAsZip") }}
                </a>
                <a
                    v-if="zipStep == 'requested'"
                    class="menu-item"
                >
                    <Spinner />
                    {{ $t("generatingZip") }}
                </a>
                <a
                    v-if="zipStep == 'error'"
                    class="menu-item"
                >
                    {{ $t("zipGenerationError") }}
                </a>
                <a
                    v-if="zipStep == 'generated' || zipStep == 'downloaded'"
                    class="menu-item willClose"
                    :href="zipUrl"
                    @click="setZipStep('downloaded')"
                >
                    {{ $t("downloadZipFile") }}
                </a>
            </template>
        </Popper>

        <transition
            enter-active-class="animated fadeIn"
            leave-active-class="animated fadeOut"
        >
            <AssetUrlForm
                v-if="isAssetUrlFormVisible"
                class="simple-panel w-full max-w-lg"
                :namespace="namespace"
            />
        </transition>
    </template>

    <template #afterDropzonePreview>
        <Loadarium name="fetchLinkedAssets" />

        <!-- We cannot use the Loadarium slot because <Dropzone> needs to see .startUpload elements -->
        <div
            v-show="!loadingInProgress.fetchLinkedAssets"
            class="w-full"
        >
            <transition-group
                class="AssetList"
                enter-active-class="animated fadeIn"
                leave-active-class="animated fadeOut"
            >
                <LinkedAssetsElement
                    v-for="asset in sortedLinkedAssets"
                    :asset="asset"
                    :gridView="gridView"
                    :key="asset.id"
                    :namespace="namespace"
                />

                <!-- Add more assets, when there's already some, with a LIST layout -->
                <!-- We can't use v-if because <Dropzone> must find .startUpload at init -->
                <div
                    v-if="showPlaceholder"
                    class="startUpload AssetElement dropzone-bordered border-dashed border-2 flex justify-start items-center p-4"
                    :class="{ hidden: !anyLinkedFile || gridView }"
                    key="uploadElementList"
                >
                    <Icon
                        class="h-10 w-10 text-gray-400"
                        name="PlusCircle"
                    />
                    <div class="text-gray-600 flex flex-wrap whitespace-no-wrap">
                        <a class="font-medium indigo-link mx-1">
                            {{ $t("addFile") }}
                        </a>
                        {{ $t("orDragAndDrop") }}
                        {{ $t("or") }}
                        <a
                            class="button is-indigo is-small ml-1"
                            @click.stop="openOffPanel('assetsLibrary')"
                        >
                            {{ $t("linkAssetFromLibrary") }}
                        </a>
                    </div>
                </div>

                <!-- Add more assets, when there's already some, with a GRID layout -->
                <!-- We can't use v-if because <Dropzone> must find .startUpload at init -->
                <div
                    v-if="showPlaceholder"
                    class="startUpload AssetElement GridView dropzone-bordered border-dashed border-2 flex justify-center items-center"
                    :class="{ hidden: !anyLinkedFile || !gridView }"
                    key="uploadElementGrid"
                >
                    <Icon
                        class="mx-auto h-12 w-12 text-gray-400"
                        name="PlusCircle"
                    />
                    <p class="mt-1 text-gray-600 whitespace-no-wrap">
                        <a class="font-medium indigo-link">
                            {{ $t("addFile") }}
                        </a>
                        {{ $t("orDragAndDrop") }}
                    </p>
                    <p>
                        {{ $t("or") }}
                        <a
                            class="button is-indigo is-small mt-1"
                            @click.stop="openOffPanel('assetsLibrary')"
                        >
                            {{ $t("linkAssetFromLibrary") }}
                        </a>
                    </p>
                </div>
            </transition-group>

            <!-- Add first asset, when there's no linked asset yet -->
            <!-- We can't use v-if because <Dropzone> must find .startUpload at init -->
            <div
                v-show="!anyLinkedFile"
                class="startUpload dropzone-bordered help-text mt-4"
                :class="{
                    'mx-0': !gridView,
                    'max-w-none': !gridView,
                }"
            >
                <div class="help-text-title">
                    <Icon
                        class="help-text-icon"
                        name="Asset"
                    />
                    <span>{{ $t("noLinkedFile") }}</span>
                </div>
                <div>
                    {{ $t("dragHereToUpload") }}
                    <a
                        v-show="!usageLimitReached('asset_storage')"
                        class="lowercase font-medium mx-1"
                        type="button"
                    >
                        {{ $t("linkAssetFromComputer") }}
                    </a>
                    {{ $t("or") }}
                    <a
                        class="lowercase font-medium mx-1"
                        @click.stop="openOffPanel('assetsLibrary')"
                    >
                        {{ $t("linkAssetFromLibrary") }}
                    </a>
                </div>
            </div>
        </div>

        <OffPanel
            name="assetsLibrary"
            position="left"
            width="75%"
        >
            <div slot="offPanelTitle">{{ $t("searchInMediaLibrary") }}</div>
            <div slot="offPanelBody">
                <AssetList
                    context="picker"
                    :isAssetLinked="isAssetLinked"
                    @link="linkAsset"
                />
            </div>
        </OffPanel>
    </template>
</DropZone>
</template>

<script>
import _ from "lodash"
import $ from "jquery"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import urls from "@js/urls"
import {
    DZ_PREVIEW_TEMPLATE_WITH_IMAGE,
    DZ_PREVIEW_TEMPLATE_WITHOUT_IMAGE,
} from "@js/dropzoneTemplates"
import LinkedAssetsStoreMapper from "./LinkedAssetsStoreMapper"
import PilotMixin from "@components/PilotMixin"
import AssetConverter from "@js/AssetConverter"
import { getInMemoryApiSource } from "@js/apiSource"

import UsageLimitAlert from "@components/UsageLimitAlert.vue"
import DropZone from "@components/DropZone.vue"

import AssetUrlForm from "./AssetUrlForm.vue"
import AssetList from "../list/AssetList.vue"
import LinkedAssetsElement from "./LinkedAssetsElement.vue"

export default {
    name: "LinkedAssets",
    mixins: [PilotMixin, LinkedAssetsStoreMapper],
    components: {
        UsageLimitAlert,
        DropZone,

        AssetUrlForm,
        AssetList,
        LinkedAssetsElement,
    },
    props: {
        gridView: {
            type: Boolean,
            default: true,
        },
        showPlaceholder: {
            type: Boolean,
            default: true,
        },
    },
    data: () => ({
        dropzoneFilesCount: 0,
        assetConverter: new AssetConverter(),
    }),
    computed: {
        ...mapState("loading", ["loadingInProgress"]),
        ...mapGetters("usageLimits", ["usageLimitReached"]),
        previewTemplate() {
            return this.gridView
                ? DZ_PREVIEW_TEMPLATE_WITH_IMAGE
                : DZ_PREVIEW_TEMPLATE_WITHOUT_IMAGE
        },
        anyLinkedFile() {
            return this.linkedAssets.length || this.dropzoneFilesCount
        },
        sortedLinkedAssets() {
            return _.reverse(_.sortBy(this.linkedAssets, (linkedAsset) => linkedAsset.created_at))
        },
    },
    methods: {
        ...mapMutations("assetList", ["setApiSource"]),
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
    },
    created() {
        this.setApiSource(getInMemoryApiSource(urls.assetsLibrary))

        /***********************
         * Leave page with ungenerated zip
         ************************/
        this.onBeforeUnload = () => {
            if (this.zipStep == "requested" || this.zipStep == "generated") {
                return this.$t("zipGeneratingDoNotLeave")
            }
        }
        $(window).on("beforeunload", this.onBeforeUnload)
    },
    beforeDestroy() {
        $(window).off("beforeunload", this.onBeforeUnload)
    },
    i18n: {
        messages: {
            fr: {
                addOneOrMoreFiles: "Ajouter un ou plusieurs fichier(s)",
                asExternalLink: "Comme lien externe",
                downloadAsZip: "Télécharger tous les fichiers (zip)",
                downloadZipFile: "Télécharger le zip",
                dragHereToUpload: "Glissez-déposez des fichiers ou sélectionnez les",
                generatingZip: "Génération du zip en cours (merci de patienter)",
                noLinkedFile: "Aucun fichier lié",
                orBrowse: "sélectionnez sur votre ordinateur",
                refresh: "Actualiser",
                zipGeneratingDoNotLeave:
                    "Vous avez demandé la génération d'un zip, ce zip sera perdu si vous quittez cette page",
                zipGenerationError: "Erreur de génération du zip",
            },
            en: {
                addOneOrMoreFiles: "Add one or more file (s)",
                asExternalLink: "External link",
                downloadAsZip: "Download all files (zip)",
                downloadZipFile: "Download zip file",
                dragHereToUpload: "Drag&drop files or select them",
                generatingZip: "Generating zip file, please wait",
                noLinkedFile: "No linked file",
                refresh: "Reload",
                zipGeneratingDoNotLeave:
                    "You have requested the generation of a zip, this zip will be lost if you leave this page",
                zipGenerationError: "Error during zip generation",
            },
        },
    },
}
</script>
