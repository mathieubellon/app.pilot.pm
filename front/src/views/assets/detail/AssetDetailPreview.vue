<template>
<div
    v-if="asset.id"
    class="AssetDetailPreview bg-white border border-gray-200 rounded mb-4"
>
    <DropZone
        v-if="asset.is_file_asset"
        :assetId="asset.id"
        clickable=".startUpload"
        :maxNumberOfFiles="1"
        @vdropzone-file-added="onFileAdded"
        @vdropzone-success="onUploadSuccess"
        @vdropzone-total-upload-progress="onTotalUploadProgress"
    >
        <div
            v-if="asset.is_assembly_executing"
            class="AssetPreview__assemblyExecuting"
            slot="beforeDropzonePreview"
        >
            {{ $t("assemblyExecuting") }}
        </div>

        <div
            v-show="!isUploadingFile"
            class="w-full"
            slot="afterDropzonePreview"
        >
            <AssetPreview
                :asset="asset"
                context="detail"
            />

            <div class="startUpload dropzone-bordered w-full mt-4 p-3">
                <div class="text-center">
                    <p class="mt-1 text-sm text-gray-600 whitespace-no-wrap">
                        <Icon
                            class="text-gray-400 -mt-1"
                            name="Upload"
                        />
                        <a class="font-medium indigo-link">
                            {{ $t("addNewVersion") }}
                        </a>
                        {{ $t("orDragAndDrop") }}
                    </p>
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
                <span>{{ $t("downloadOriginal", { size: humanFileSize(asset.size) }) }}</span>
            </a>
        </div>
    </DropZone>

    <div
        v-else
        class="Asset_IsExternalLink"
    >
        {{ $t("thisIsALink") }}
        <div>
            <a :href="asset.file_url">{{ asset.name }}</a>
        </div>
    </div>

    <!--
    <div v-if="asset.is_file_asset">
        <a class="text-gray-400" @click.prevent="openOffPanel('assetInfos')">
            <span v-if="assetConverter.getConversionStatusAborted">{{ $t('conversionStatusAborted') }}</span>
            <template v-else>
                <span v-if="conversionData.status"> {{ conversionData.status }}</span>
                <span v-if="conversionData.message"> {{ conversionData.message }}</span>
                <span v-else>{{ $t('conversionDataUnavailable') }}</span>
            </template>
        </a>
    </div>

    <OffPanel name="assetInfos">
        <div slot="offPanelTitle">{{ $t('conversionInformations') }}</div>
        <div slot="offPanelBody">
            <div class="assetInfo">
                <button @click.prevent="assetConverter.startConversion(asset)" class="button hollow expanded">
                    {{ $t('convert') }}
                </button>
                <button @click.prevent="assetConverter.getConversionStatus(asset)" class="button hollow expanded">
                    {{ $t('convertCheckStatus') }}
                </button>

                <div v-for="(value, index) in asset">
                    <div>
                        <div><strong>{{index}}</strong></div>
                        <pre>{{value}}</pre>
                    </div>
                </div>
            </div>
        </div>
    </OffPanel>
    --></div>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { getFileProperties } from "@js/assetsUtils"
import { humanFileSize } from "@js/localize.js"
import PilotMixin from "@components/PilotMixin"

import DropZone from "@components/DropZone.vue"
import AssetPreview from "../AssetPreview.vue"

export default {
    name: "AssetDetailPreview",
    mixins: [PilotMixin],
    components: {
        DropZone,
        AssetPreview,
    },
    data: () => ({
        humanFileSize,
    }),
    computed: {
        ...mapState("assetDetail", ["asset", "isUploadingFile", "assetConverter"]),
        conversionData() {
            return _.get(this.asset, "conversions.conversionData", {})
        },
    },
    methods: {
        ...mapMutations("assetDetail", ["setIsUploadingFile"]),
        ...mapActions("assetDetail", ["partialUpdateAsset"]),
        onFileAdded() {
            this.setIsUploadingFile(true)
        },
        onUploadSuccess(file) {
            let assetData = getFileProperties(file)
            assetData.fileChanged = true

            this.partialUpdateAsset(assetData).then((response) => {
                // Updating the asset will start a new transloadit conversion.
                // We can start polling it now.
                this.assetConverter.waitForAssetConversionStatus(this.asset)
                file.previewElement.outerHTML = ""
                this.setIsUploadingFile(false)
            })
        },
        onTotalUploadProgress(uploadProgress) {
            this.assetConverter.onTotalUploadProgress(uploadProgress)
        },
    },
    i18n: {
        messages: {
            fr: {
                addNewVersion: "Envoyer une nouvelle version",
                conversionDataUnavailable: "Pas de données de conversion",
                conversionInformations: "Informations détaillées",
                conversionStatusAborted:
                    "La génération de métadonnées prend trop de temps. J'arrête de vérifier pour le moment. Vous pouvez télécharger l'original.",
                convert: "Lancer une conversion",
                convertCheckStatus: "Vérifier l'état de la conversion",
                downloadOriginal: "Télécharger l'original ({size})",
                thisIsALink: "Ce fichier est un lien vers un fichier externe.",
            },
            en: {
                addNewVersion: "Upload new version",
                conversionDataUnavailable: "Conversion data unavailable",
                conversionStatusAborted:
                    "Metadata generation takes too much time. I won't check anymore for now. You can download the original file.",
                conversionInformations: "Asset details",
                convert: "Make conversion",
                convertCheckStatus: "Check conversion state",
                downloadOriginal: "Download the original ({size})",
                thisIsALink: "This is an link to an external file.",
            },
        },
    },
}
</script>
