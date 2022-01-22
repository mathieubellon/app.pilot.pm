<template>
<div
    v-if="asset"
    class="AssetPreview"
    :class="[
        context,
        {
            AssetPreview__assemblyExecuting: asset.is_assembly_executing,
            'cursor-pointer': context != 'detail' && context != 'itemMedia' && context != 'shared',
        },
    ]"
    @click="goToDetailView()"
>
    <template v-if="!asset.is_assembly_executing">
        <!-- Image -->
        <template v-if="asset.filetype === 'image'">
            <img
                v-if="imageUrl"
                :alt="asset.name"
                :src="imageUrl"
            />
            <Icon
                v-else
                name="FileImage"
            />
        </template>

        <!-- PDF -->
        <template
            v-else-if="asset.filetype === 'pdf'"
            class="AssetPreview__pdf"
        >
            <VuePDFjs
                v-if="showPDFView && asset.file_url"
                :pdfpath="asset.file_url"
            />
            <img
                v-else-if="imageUrl"
                :alt="asset.name"
                :src="imageUrl"
            />
            <Icon
                v-else
                name="FilePDF"
            />
        </template>

        <!-- Video -->
        <!-- We use @click.stop to allow interraction with the media player without triggering
        goToDetailView() on the root element -->
        <div
            v-else-if="asset.filetype === 'video'"
            class="AssetPreview__video"
            :key="mediaPlayerSource"
            @click.stop
        >
            <VuePlyr v-if="showMediaPlayer && mediaPlayerSource">
                <video controls>
                    <source
                        :src="mediaPlayerSource"
                        type="video/mp4"
                    />
                </video>
            </VuePlyr>

            <img
                v-else-if="asset.cover_url"
                :alt="asset.name"
                :src="asset.cover_url"
            />

            <Icon
                v-else
                name="FileVideo"
            />
        </div>

        <!-- Audio -->
        <!-- We use @click.stop to allow interraction with the media player without triggering
        goToDetailView() on the root element -->
        <div
            v-else-if="asset.filetype === 'audio'"
            class="AssetPreview__audio"
            :key="mediaPlayerSource"
            @click.stop
        >
            <VuePlyr v-if="showMediaPlayer && mediaPlayerSource">
                <audio controls>
                    <source
                        :src="mediaPlayerSource"
                        type="audio/mp3"
                    />
                </audio>
            </VuePlyr>

            <Icon
                v-else
                name="FileAudio"
            />
        </div>

        <!-- Excel -->
        <template v-else-if="asset.extension === 'xlsx' || asset.extension === 'xls'">
            <iframe
                v-if="showOfficeView && asset.file_url"
                frameborder="0"
                :id="asset.id"
                marginheight="0"
                marginwidth="0"
                scrolling="no"
                :src="
                    'https://view.officeapps.live.com/op/view.aspx?src=' + encodeURI(asset.file_url)
                "
                :title="'Preview ' + asset.title"
                width="100%"
            ></iframe>
            <Icon
                v-else
                name="FileExcel"
            />
        </template>
        <!-- Word -->
        <template v-else-if="asset.extension === 'docx' || asset.extension === 'doc'">
            <iframe
                v-if="showOfficeView && asset.file_url"
                frameborder="0"
                :id="asset.id"
                marginheight="0"
                marginwidth="0"
                scrolling="no"
                :src="
                    'https://view.officeapps.live.com/op/view.aspx?src=' + encodeURI(asset.file_url)
                "
                :title="'Preview ' + asset.title"
                width="100%"
            ></iframe>
            <Icon
                v-else
                name="FileWord"
            />
        </template>
        <!-- Powerpoint -->
        <template v-else-if="asset.extension === 'pptx' || asset.extension === 'ppt'">
            <iframe
                v-if="showOfficeView && asset.file_url"
                frameborder="0"
                :id="asset.id"
                marginheight="0"
                marginwidth="0"
                scrolling="no"
                :src="
                    'https://view.officeapps.live.com/op/view.aspx?src=' + encodeURI(asset.file_url)
                "
                :title="'Preview ' + asset.title"
                width="100%"
            ></iframe>
            <Icon
                v-else
                name="FilePowerpoint"
            />
        </template>
        <!-- Archive -->
        <div v-else-if="asset.extension === 'zip'">
            <Icon name="FileZIP" />
        </div>
        <!-- Other files -->
        <div v-else>
            <Icon name="FileDefault" />
        </div>
    </template>
</div>
</template>

<script>
import _ from "lodash"
import PilotMixin from "@components/PilotMixin"
import { VuePlyr } from "vue-plyr"
import VuePDFjs from "./VuePDFjs"

export default {
    name: "AssetPreview",
    mixins: [PilotMixin],
    components: {
        VuePlyr,
        VuePDFjs,
    },
    props: {
        asset: {
            type: Object,
            required: false,
        },
        // Can be "list", "detail", "linked", "itemMedia", "shared"
        context: String,
    },
    computed: {
        firstWorkingUrl() {
            return _.get(this.asset, "working_urls.0", null)
        },
        imageUrl() {
            // We always use the small cover image in lists.
            // In other contexts, we try to use the larger image, if it exists
            let largeImage = this.firstWorkingUrl ? this.firstWorkingUrl : this.asset.cover_url
            return this.context == "list" ? this.asset.cover_url : largeImage
        },
        mediaPlayerSource() {
            return this.firstWorkingUrl ? this.firstWorkingUrl : this.asset.file_url
        },
        showPDFView() {
            // Use the PDF view only on detail context
            return this.context == "detail"
        },
        showMediaPlayer() {
            // Use the media player everywhere except in list
            return (
                this.context == "detail" ||
                this.context == "linked" ||
                this.context == "itemMedia" ||
                this.context == "shared"
            )
        },
        showOfficeView() {
            // Use the office view only on detail context
            return this.context == "detail"
        },
    },
    methods: {
        goToDetailView() {
            if (
                this.context != "detail" &&
                this.context != "itemMedia" &&
                this.context != "shared"
            ) {
                this.$router.push({ name: "assetDetail", params: { id: this.asset.id } })
            }
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";
@import "~@sass/include_media.scss";

.AssetPreview.list {
    width: 80px;
    height: 50px;
    overflow-y: hidden;
    overflow-x: hidden;
    background-color: $gray-lighter;
    border-radius: 3px;
    margin-right: 1em;
    flex-shrink: 0;
    flex-grow: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    transition: height 0.2s, width 0.3s;

    svg {
        width: 30px;
        height: 40px;
    }

    img {
        width: 80px;
        height: auto;
    }

    @include media(">phone", "<=tablet") {
        width: 100%;
        height: 200px;
    }
}

.AssetPreview.detail {
    width: 100%;
    margin-right: 0;
    align-items: flex-start;
    display: flex;
    justify-content: center;

    img {
        max-width: 100%;
        max-height: 100%;
    }

    iframe {
        height: 80vh;
    }
}

.AssetElement.GridView {
    .AssetPreview {
        width: 100%;
        height: 200px;
        max-height: 200px;
        background-color: $gray-lighter;
        overflow-y: hidden;
        display: flex;
        justify-content: center;
        align-items: flex-start;
        margin-right: 0;

        img {
            width: inherit;
        }
    }
}

.AssetPreview__assemblyExecuting {
    background-color: $purple !important;
    color: #fefefe;
    font-size: 0.8em;
    font-weight: bold;

    padding: 0 1em;
    border-radius: 3px;
}

.AssetPreview__video {
    display: flex;
    justify-content: center;
}
</style>
