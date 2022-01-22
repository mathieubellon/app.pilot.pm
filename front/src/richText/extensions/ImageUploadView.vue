<template>
<div class="ImageUploadView flex items-center justify-center whitespace-normal">
    <div
        v-if="converting"
        class="ImageUploadView__assemblyExecuting AssetElement GridView"
    >
        <div class="AssetPreview__assemblyExecuting h-full flex flex-col justify-evenly">
            <div>
                {{ $t("assemblyExecuting") }}
            </div>
            <div>
                {{ file.name }}
            </div>
        </div>
    </div>

    <DropZone
        v-show="uploading"
        ref="dropzone"
        :clickable="false"
        :maxNumberOfFiles="1"
        :previewTemplate="previewTemplate"
        @vdropzone-file-signed="onFileSigned"
        @vdropzone-success="onUploadSuccess"
    />

    <div
        v-if="!uploading && !converting"
        class="ImageUploadView__assemblyExecuting AssetElement GridView"
    >
        <div class="AssetPreview__assemblyExecuting h-full flex flex-col justify-center">
            <div>
                {{ $t("uploading") }}
            </div>
        </div>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import urls from "@js/urls"
import { $http } from "@js/ajax"
import { DZ_PREVIEW_TEMPLATE_WITH_IMAGE } from "@js/dropzoneTemplates"
import { getFileProperties, getImageAttrsFromAsset } from "@js/assetsUtils"
import AssetConverter from "@js/AssetConverter"

import DropZone from "@components/DropZone.vue"

export default {
    name: "ImageUploadView",
    props: ["node", "editor", "getPos", "updateAttrs"],
    components: {
        DropZone,
    },
    data: () => ({
        previewTemplate: DZ_PREVIEW_TEMPLATE_WITH_IMAGE,
        assetConverter: new AssetConverter(),
        converting: false,
        uploading: false,
    }),
    computed: {
        file() {
            return this.editor.uploadedFiles[this.uploadId]
        },
        uploadId() {
            return this.node.attrs.uploadId
        },
        assetId() {
            return this.node.attrs.assetId
        },
    },
    methods: {
        onFileSigned(file) {
            this.updateAttrs({ assetId: file.assetId })
        },
        onUploadSuccess(file) {
            this.uploading = false
            this.converting = true

            let assetData = getFileProperties(file)
            _.assign(assetData, {
                assetId: file.assetId, // Temporary creation by AssetId
                content_type_id: window.pilot.contentTypes.Item.id,
                object_id: this.editor.itemId,
                in_media_library: false,
            })

            $http.post(urls.assets, assetData).then((response) => {
                let asset = response.data

                this.assetConverter.on("conversionStatusUpdate", (asset) => {
                    let schema = this.editor.schema
                    let pos = this.getPos()
                    this.editor.dispatchTransaction(
                        this.editor.state.tr.replaceRangeWith(
                            pos,
                            pos + 1,
                            schema.nodes.image.create(getImageAttrsFromAsset(asset)),
                        ),
                    )

                    this.editor.$store.commit("itemDetail/linkedAssets/prependLinkedAsset", asset)
                })

                this.assetConverter.waitForAssetConversionStatus(asset)
            })

            this.$refs.dropzone.removeFile(file)
        },
    },
    mounted() {
        if (this.file) {
            this.uploading = true
            this.$refs.dropzone.addFile(this.file)
            this.$refs.dropzone.processQueue()
            this.$refs.dropzone.removeEventListeners()
        }
    },
    i18n: {
        messages: {
            fr: {
                uploading: "Image en cours d'upload...",
            },
            en: {
                uploading: "Image uploading...",
            },
        },
    },
}
</script>

<style lang="scss">
.ImageUploadView .AssetElement {
    margin: 0;
}

.ImageUploadView__assemblyExecuting {
    height: 300px;
}
</style>
