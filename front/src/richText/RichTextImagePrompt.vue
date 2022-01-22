<template>
<Modal
    height="500px"
    :name="`imagePrompt-${editorId}`"
    width="800px"
    @opened="onModalOpened"
>
    <div class="RichTextImagePrompt">
        <div
            v-if="!isEdition"
            class="tabs mb-8 border-b justify-between"
        >
            <a
                class="tab"
                :class="{ 'is-active': currentTab == 'upload' }"
                @click="openTab('upload')"
            >
                {{ $t("from.upload") }}
            </a>
            <!-- This is absolutely brutal, but only item editors do have an associated annotationManager,
            so we only show the linked items tab when there's this props, because it means we're in an item editor. -->
            <a
                v-if="annotationManager"
                class="tab"
                :class="{ 'is-active': currentTab == 'linkedAssets' }"
                @click="openTab('linkedAssets')"
            >
                {{ $t("from.linkedAssets") }}
            </a>
            <a
                class="tab"
                :class="{ 'is-active': currentTab == 'url' }"
                @click="openTab('url')"
            >
                {{ $t("from.url") }}
            </a>
        </div>

        <div v-if="currentTab == 'linkedAssets' && !linkedAssetsImages.length">
            {{ $t("noLinkedImage") }}
        </div>
        <template v-else>
            <form
                class="w-full"
                ref="form"
                @keydown.enter.prevent="$emit('submit')"
                @keydown.escape.prevent="$modal.hide(`imagePrompt-${editorId}`)"
                @submit.prevent="$emit('submit')"
            >
                <template v-if="!isEdition">
                    <div v-if="currentTab == 'upload'">
                        <div v-if="isAssemblyError || assetConverter.getConversionStatusAborted">
                            {{ $t("assemblyError") }}
                        </div>
                        <div v-else-if="isAssemblyRunning">
                            <Spinner />
                            {{ $t("assemblyExecuting") }}
                        </div>
                        <img
                            v-else-if="selectedAsset"
                            :src="selectedAsset.cover_url"
                        />
                        <DropZone
                            v-else
                            class="dropzone-bordered"
                            :maxNumberOfFiles="1"
                            :previewTemplate="previewTemplate"
                            @vdropzone-success="onUploadSuccess"
                        >
                            <template #dropzoneMessage>
                                <div class="text-center">
                                    <Icon
                                        class="mx-auto h-10 w-10 text-gray-400"
                                        name="Image"
                                    />
                                    <p class="mt-1 text-sm text-gray-600 whitespace-no-wrap">
                                        <a class="font-medium indigo-link">
                                            {{ $t("addFile") }}
                                        </a>
                                        {{ $t("orDragAndDrop") }}
                                    </p>
                                    <p class="mt-1 text-xs text-gray-500">
                                        {{ $t("acceptedFileTypes") }}
                                    </p>
                                </div>
                            </template>
                        </DropZone>
                    </div>
                    <div
                        v-if="currentTab == 'linkedAssets'"
                        class="RichTextImagePrompt__linkedAssets"
                    >
                        <a
                            v-for="asset in linkedAssetsImages"
                            :class="{ selected: selectedAsset == asset }"
                            @click="selectLinkedAsset(asset)"
                        >
                            <img :src="asset.cover_url" />
                            {{ asset.name }}
                        </a>
                    </div>
                    <div v-if="currentTab == 'url'">
                        {{ $t("imageSrc") }}:
                        <CharInputWrapping v-model="imageAttrs.src" />
                    </div>
                </template>

                <template v-if="imageAttrs.src">
                    {{ $t("caption") }}:
                    <CharInputWrapping v-model="imageAttrs.caption" />
                    {{ $t("title") }}:
                    <CharInputWrapping v-model="imageAttrs.title" />
                    {{ $t("imageAltText") }}:
                    <CharInputWrapping v-model="imageAttrs.alt" />
                </template>

                <div class="mt-2">
                    <button
                        v-show="imageAttrs.src"
                        class="button is-blue"
                        type="submit"
                    >
                        {{ $t("ok") }}
                    </button>
                    <button
                        class="button"
                        type="button"
                        @click="$modal.hide(`imagePrompt-${editorId}`)"
                    >
                        {{ $t("cancel") }}
                    </button>
                </div>
            </form>
        </template>
    </div>
</Modal>
</template>

<script>
import _ from "lodash"
import $ from "jquery"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { DZ_PREVIEW_TEMPLATE_WITH_IMAGE } from "@js/dropzoneTemplates"
import { getImageAttrsFromAsset } from "@js/assetsUtils"
import AssetConverter from "@js/AssetConverter"

import Spinner from "@components/Spinner.vue"
import DropZone from "@components/DropZone.vue"
import Icon from "@components/Icon.vue"
import CharInputWrapping from "@components/forms/widgets/CharInputWrapping"

export default {
    name: "RichTextImagePrompt",
    components: {
        Icon,
        Spinner,
        DropZone,
        CharInputWrapping,
    },
    inject: ["editorId", "annotationManager"],
    props: {
        imageAttrs: Object,
    },
    data: () => ({
        isEdition: false,

        currentTab: "upload",
        selectedAsset: null,

        previewTemplate: DZ_PREVIEW_TEMPLATE_WITH_IMAGE,
        isAssemblyRunning: false,
        isAssemblyError: false,

        assetConverter: new AssetConverter(),
    }),
    computed: {
        ...mapState("itemDetail/linkedAssets", ["linkedAssets"]),
        linkedAssetsImages() {
            return this.linkedAssets.filter(
                (asset) => asset.is_image && !asset.is_assembly_executing,
            )
        },
    },
    methods: {
        ...mapActions("itemDetail/linkedAssets", ["addUploadedAsset"]),
        onModalOpened() {
            this.isEdition = this.imageAttrs.src != ""
            this.selectedAsset = null
            if (!this.isEdition) {
                this.openTab("upload")
            }
        },
        openTab(tab) {
            _.assign(this.imageAttrs, {
                src: "",
                caption: "",
                title: "",
                alt: "",
            })
            this.selectedAsset = null
            this.currentTab = tab
        },
        selectLinkedAsset(asset) {
            this.selectedAsset = asset
            _.assign(this.imageAttrs, getImageAttrsFromAsset(asset))
        },
        onUploadSuccess(file) {
            this.addUploadedAsset(file).then((asset) => {
                // Updating the asset will start a new transloadit conversion.
                // We can start polling it now.
                this.isAssemblyRunning = true
                this.assetConverter.waitForAssetConversionStatus(asset)
            })
        },
        onConversionStatusUpdate(asset) {
            if (asset.is_assembly_completed) {
                this.isAssemblyRunning = false
                this.selectLinkedAsset(asset)
            } else if (asset.is_assembly_error) {
                this.isAssemblyRunning = false
                this.isAssemblyError = true
            }
        },
    },
    created() {
        this.assetConverter.on("conversionStatusUpdate", this.onConversionStatusUpdate)
    },
    mounted() {
        // Move the modal out of the menubar to fix z-index + position:sticky issues
        $(this.$el).appendTo("body")
    },
    beforeDestroy() {
        this.$modal.hide(`imagePrompt-${this.editorId}`)

        // Elements appended to body must be removed manually, because Vue.js won't do it automatically.
        if (this.$el) {
            this.$el.remove()
        }
    },
    i18n: {
        messages: {
            fr: {
                acceptedFileTypes: "Image (PNG, JPG, GIF, ... ) ou PDF",
                caption: "Légende",
                from: {
                    upload: "Depuis votre ordinateur",
                    linkedAssets: "Depuis les fichiers liés",
                    url: "Depuis une URL externe",
                },
                imageAltText: "Texte alternatif",
                imageSrc: "Url vers une image",
                noLinkedImage: "Il n'y a pas d'image dans les fichiers liés",
            },
            en: {
                acceptedFileTypes: "Image (PNG, JPG, GIF, ... ) or PDF",
                caption: "Caption",
                from: {
                    upload: "From your computer",
                    linkedAssets: "From the linked assets",
                    url: "From an external url",
                },
                imageAltText: "Alternative text",
                imageSrc: "Url to an image",
                noLinkedImage: "There's no image in the linked assets",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.RichTextImagePrompt {
    height: 500px;
    @apply p-8 overflow-y-auto;
}

.RichTextImagePrompt__linkedAssets {
    @apply flex flex-wrap;

    a {
        @apply border-2 mr-4 overflow-hidden;
        width: 100px;

        img {
            max-width: 100%;
            max-height: 100px;
            object-fit: contain;
            object-position: center top;
        }

        &.selected {
            border-color: $red500;
        }
    }

    img {
        width: 100%;
    }
}
</style>
