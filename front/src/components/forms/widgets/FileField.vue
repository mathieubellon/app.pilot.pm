<template>
<div class="FileField">
    <div class="form__field">
        <span>{{ label }}</span>

        <div v-if="deletedFile">
            {{ $t("saveToConfirmDeletion") }}
            <br />
            {{ $t("or") }}
            <br />
            <a @click="cancelFileDeletion">{{ $t("cancelFileDeletion") }}</a>
        </div>

        <template v-else>
            <div v-if="currentFile">
                <img :src="currentFile" />
            </div>

            <DropZone
                ref="dropzone"
                :acceptFileFunction="acceptFile"
                :buttonText="buttonText"
                :maxNumberOfFiles="1"
                :previewTemplate="previewTemplate"
                :resizeHeight="height"
                :resizeWidth="width"
                :thumbnailHeight="height"
                :thumbnailWidth="width"
                @vdropzone-files-added="setUploadInProgress(true)"
                @vdropzone-queue-complete="setUploadInProgress(false)"
                @vdropzone-success="onUploadSuccess"
            />

            <div v-if="currentFile">
                {{ $t("or") }}
                <br />
                <button
                    class="red-link text-sm font-medium"
                    type="button"
                    @click="deleteFile()"
                >
                    {{ $t("deleteFile") }}
                </button>
            </div>
        </template>
    </div>
</div>
</template>

<script>
import { $http } from "@js/ajax.js"
import { DZ_PREVIEW_TEMPLATE_WITHOUT_IMAGE } from "@js/dropzoneTemplates"

import DropZone from "@components/DropZone"

export default {
    name: "FileField",
    components: {
        DropZone,
    },
    props: {
        currentFile: String,
        label: String,
        acceptUrl: Object,
        buttonText: String,
        height: Number,
        width: Number,
    },
    data: () => ({
        uploadInProgress: false,
        deletedFile: null,
        previewTemplate: DZ_PREVIEW_TEMPLATE_WITHOUT_IMAGE,
    }),
    methods: {
        acceptFile(file, done) {
            let fileInfo = {
                contentType: file.type,
            }
            /* Signature for Ireland AWS Region */
            $http.post(this.acceptUrl, fileInfo).then((response) => {
                file.policy = response.data
                done()
            })
        },
        setUploadInProgress(uploadInProgress) {
            this.uploadInProgress = uploadInProgress
        },
        onUploadSuccess(file) {
            this.$emit("input", file.policy.key)
        },
        deleteFile() {
            this.deletedFile = this.currentFile
            this.$emit("input", "DELETE")
        },
        cancelFileDeletion() {
            this.deletedFile = null
            this.$emit("input", null)
        },
        reset() {
            if (this.$refs.dropzone) this.$refs.dropzone.removeAllFiles()
            this.deletedFile = null
        },
    },
    i18n: {
        messages: {
            fr: {
                cancelFileDeletion: "Annuler la suppression",
                deleteFile: "Supprimer le fichier actuel ",
                saveToConfirmDeletion: 'Cliquez sur "Enregistrer" pour confirmer la suppression',
            },
            en: {
                cancelFileDeletion: "Cancel deletion",
                deleteFile: "Delete the current file",
                saveToConfirmDeletion: 'Click on "save" to confirm the deletion',
            },
        },
    },
}
</script>

<style lang="scss">
.FileField {
    .dropzone {
        align-items: flex-start;
        padding: 0;
    }
}
</style>
