<template>
<div class="AssetUploader">
    <DropZone
        class="dropzone-bordered"
        :maxNumberOfFiles="maxNumberOfFiles"
        :previewTemplate="previewTemplate"
        @vdropzone-files-added="emitUploadInProgress(true)"
        @vdropzone-queue-complete="emitUploadInProgress(false)"
        @vdropzone-removed-file="removeFileFromQueue"
        @vdropzone-success="onUploadSuccess"
    >
        <template #dropzoneMessage>
            <div class="text-center">
                <Icon
                    class="mx-auto h-10 w-10 text-gray-400"
                    name="File"
                />
                <p class="mt-1 text-sm text-gray-600 whitespace-no-wrap">
                    <a class="font-medium indigo-link">
                        {{ $t("addFile") }}
                    </a>
                    {{ $t("orDragAndDrop") }}
                </p>
            </div>
        </template>
    </DropZone>
</div>
</template>

<script>
import _ from "lodash"
import { getFileProperties } from "@js/assetsUtils"
import { DZ_PREVIEW_TEMPLATE_WITHOUT_IMAGE } from "@js/dropzoneTemplates"
import DropZone from "@components/DropZone"
import Icon from "@components/Icon.vue"

export default {
    name: "AssetUploader",
    components: {
        DropZone,
        Icon,
    },
    props: {
        value: Array,
        maxNumberOfFiles: Number,
    },
    data: () => ({
        previewTemplate: DZ_PREVIEW_TEMPLATE_WITHOUT_IMAGE,
        uploadInProgress: false,
    }),
    methods: {
        emitUploadInProgress(uploadInProgress) {
            this.uploadInProgress = uploadInProgress
            this.$emit("uploadInProgress", uploadInProgress)
        },
        onUploadSuccess(file) {
            let assetData = getFileProperties(file)
            _.assign(assetData, {
                assetId: file.assetId, // Temporary creation by AssetId
                in_media_library: false,
            })

            this.value.push(assetData)
            this.$emit("input", this.value)
        },
        removeFileFromQueue(eventPayload) {
            _.remove(this.value, { uuid: eventPayload.policy.uuid })
            this.$emit("input", this.value)
        },
    },
}
</script>
