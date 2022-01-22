<template>
<div class="dropzone">
    <!--If Dropzone does not find a dz-message element it will insert its own,
    this not what we want, so we always declare one-->
    <div class="dz-message">
        <span
            v-if="buttonText"
            class="dz-upload-button"
        >
            {{ buttonText }}
        </span>
        <slot name="dropzoneMessage" />
    </div>
    <slot name="beforeDropzonePreview" />
    <div
        class="dropzone-previews"
        ref="dropzonePreviews"
    />
    <slot name="afterDropzonePreview" />
</div>
</template>

<script>
import _ from "lodash"
import Dropzone from "dropzone"
import { DZ_PREVIEW_TEMPLATE_WITH_IMAGE } from "@js/dropzoneTemplates"
import { getAxiosErrorMessage } from "@js/errors"
import { signFileForAssetUpload } from "@js/assetsUtils"

Dropzone.autoDiscover = false

export default {
    props: {
        url: {
            type: String,
            default: window.pilot.djangoSettings.AWS_S3_BASE_URL,
        },
        assetId: {
            type: Number,
            default: null,
        },
        acceptFileFunction: {
            type: Function,
            default: null,
        },
        clickable: {
            type: [Boolean, String],
            default: true,
        },
        paramName: {
            type: String,
            default: "file",
        },
        acceptedFileTypes: {
            type: String,
        },
        buttonText: {
            type: String,
            default: "",
        },
        thumbnailHeight: {
            type: Number,
            default: null,
        },
        thumbnailWidth: {
            type: Number,
            default: null,
        },
        showRemoveLink: {
            type: Boolean,
            default: true,
        },
        maxFileSizeInMB: {
            type: Number,
            default: 2000,
        },
        maxNumberOfFiles: {
            type: Number,
            default: 1000,
        },
        autoProcessQueue: {
            type: Boolean,
            default: true,
        },
        headers: {
            type: Object,
        },
        language: {
            type: Object,
            default: function () {
                return {}
            },
        },
        previewTemplate: {
            type: Function,
            default: DZ_PREVIEW_TEMPLATE_WITH_IMAGE,
        },
        dropzoneOptions: {
            type: Object,
            default() {
                return {}
            },
        },
        resizeWidth: {
            type: Number,
            default: null,
        },
        resizeHeight: {
            type: Number,
            default: null,
        },
        resizeMimeType: {
            type: String,
            default: null,
        },
        resizeQuality: {
            type: Number,
            default: 0.8,
        },
        resizeMethod: {
            type: String,
            default: "contain",
        },
        uploadMultiple: {
            type: Boolean,
            default: false,
        },
        parallelUploads: {
            type: Number,
            default: 10,
        },
        timeout: {
            type: Number,
            default: 36000000,
        },
        method: {
            type: String,
            default: "POST",
        },
    },
    methods: {
        addFile(file) {
            this.dropzone.addFile(file)
        },
        removeAllFiles() {
            this.dropzone.removeAllFiles(true)
        },
        processQueue() {
            this.dropzone.processQueue()
        },
        removeFile(file) {
            this.dropzone.removeFile(file)
        },
        removeEventListeners() {
            this.dropzone.removeEventListeners()
        },
        acceptFileForAsset(file, done) {
            signFileForAssetUpload(file, this.assetId)
                .then((file) => {
                    this.$emit("vdropzone-file-signed", file)
                    done()
                })
                .catch((error) => {
                    this.dropzone.options.error(file, getAxiosErrorMessage(error))
                })
        },
    },
    computed: {
        languageSettings() {
            let defaultValues = {
                dictDefaultMessage: this.buttonText,
                dictCancelUpload: this.$t("cancelUpload"),
                dictCancelUploadConfirmation: this.$t("cancelUploadConfirmation"),
                dictFallbackMessage: "Your browser does not support drag and drop file uploads.",
                dictFallbackText:
                    "Please use the fallback form below to upload your files like in the olden days.",
                dictFileTooBig:
                    "File is too big ({{filesize}}MiB). Max filesize: {{maxFilesize}}MiB.",
                dictInvalidFileType: `You can't upload files of this type.`,
                dictMaxFilesExceeded: "You can not upload any more files. (max: {{maxFiles}})",
                dictRemoveFile: this.$t("remove"),
                dictRemoveFileConfirmation: null,
                dictResponseError: "Server responded with {{statusCode}} code.",
            }

            return _.defaults(defaultValues, this.language)
        },
    },
    mounted() {
        //   The 'accept' method is triggered before file is uploaded. We use it to request a signature.
        //   The endpoint return a 'policy' object which is added to the file object.
        //   We then proceed to send a request to AWS. Doing so we unpack the policy object as a formData array and POST the request.
        let acceptFileFunction = this.acceptFileFunction
            ? this.acceptFileFunction
            : (file, done) => this.acceptFileForAsset(file, done)

        this.dropzone = new Dropzone(this.$el, {
            clickable: this.clickable,
            paramName: this.paramName,
            thumbnailWidth: this.thumbnailWidth,
            thumbnailHeight: this.thumbnailHeight,
            maxFiles: this.maxNumberOfFiles,
            maxFilesize: this.maxFileSizeInMB,
            addRemoveLinks: this.showRemoveLink,
            acceptedFiles: this.acceptedFileTypes,
            autoProcessQueue: this.autoProcessQueue,
            headers: this.headers,
            previewTemplate: this.previewTemplate(this),
            dictDefaultMessage: this.languageSettings.dictDefaultMessage,
            dictCancelUpload: this.languageSettings.dictCancelUpload,
            dictCancelUploadConfirmation: this.languageSettings.dictCancelUploadConfirmation,
            dictFallbackMessage: this.languageSettings.dictFallbackMessage,
            dictFallbackText: this.languageSettings.dictFallbackText,
            dictFileTooBig: this.languageSettings.dictFileTooBig,
            dictInvalidFileType: this.languageSettings.dictInvalidFileType,
            dictMaxFilesExceeded: this.languageSettings.dictMaxFilesExceeded,
            dictRemoveFile: this.languageSettings.dictRemoveFile,
            dictRemoveFileConfirmation: this.languageSettings.dictRemoveFileConfirmation,
            dictResponseError: this.languageSettings.dictResponseError,
            previewsContainer: this.$refs.dropzonePreviews,
            resizeWidth: this.resizeWidth,
            resizeHeight: this.resizeHeight,
            resizeMimeType: this.resizeMimeType,
            resizeQuality: this.resizeQuality,
            resizeMethod: this.resizeMethod,
            uploadMultiple: this.uploadMultiple,
            parallelUploads: this.parallelUploads,
            timeout: this.timeout,
            url: this.url,
            method: this.method,
            accept: acceptFileFunction,
        })

        // Handle the dropzone events
        this.dropzone.on("thumbnail", (file) => {
            this.$emit("vdropzone-thumbnail", file)
        })

        this.dropzone.on("addedfile", (file) => {
            this.$emit("vdropzone-file-added", file)
        })

        this.dropzone.on("addedfiles", (files) => {
            this.$emit("vdropzone-files-added", files)
        })

        this.dropzone.on("removedfile", (file) => {
            this.$emit("vdropzone-removed-file", file)
        })

        this.dropzone.on("success", (file, response) => {
            this.$emit("vdropzone-success", file, response)
        })

        this.dropzone.on("successmultiple", (file, response) => {
            this.$emit("vdropzone-success-multiple", file, response)
        })

        this.dropzone.on("error", (file, error, xhr) => {
            this.$emit("vdropzone-error", file, error, xhr)
        })

        this.dropzone.on("sending", (file, xhr, formData) => {
            // Add each policy key to formData
            for (var key in file.policy) {
                formData.append(key, file.policy[key])
            }
            // formData.append("content-type", file.type)
            this.$emit("vdropzone-sending", file, xhr, formData)
        })

        this.dropzone.on("sendingmultiple", (file, xhr, formData) => {
            this.$emit("vdropzone-sending-multiple", file, xhr, formData)
        })

        this.dropzone.on("queuecomplete", (file, xhr, formData) => {
            this.$emit("vdropzone-queue-complete", file, xhr, formData)
        })

        this.dropzone.on("totaluploadprogress", (uploadProgress, totalBytes, totalBytesSent) => {
            this.$emit(
                "vdropzone-total-upload-progress",
                uploadProgress,
                totalBytes,
                totalBytesSent,
            )
        })

        this.$emit("vdropzone-mounted")
    },
    beforeDestroy() {
        // !! VERY IMPORTANT  !!
        // Free the memory
        this.dropzone.destroy()
    },
    i18n: {
        messages: {
            fr: {
                cancelUpload: "Annuler l'envoi",
                cancelUploadConfirmation: "Etes-vous sûr de vouloir annuler l'upload ?",
                remove: "Retirer",
            },
            en: {
                cancelUpload: "Cancel upload",
                cancelUploadConfirmation: "Are you sure you want to cancel this upload ?",
                remove: "Remove",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.dropzone {
    @apply flex flex-col items-center w-full min-h-full p-4;

    .dz-message {
        @apply m-0 p-0 cursor-pointer;
    }
    .dz-upload-button {
        @apply text-lg underline text-indigo-600;
    }
    .dropzone-previews {
        width: 100%;
        display: contents;
    }
}

.dropzone-bordered {
    @apply p-6 border-2 border-gray-300 border-dashed rounded-md cursor-pointer;

    &:hover {
        @apply bg-indigo-50 border-gray-400;
    }
}
</style>
