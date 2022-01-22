<template>
<div
    class="AssetElement relative"
    :class="{ GridView: gridView }"
>
    <AssetPreview
        :asset="asset"
        :context="gridView ? 'linked' : 'list'"
    />

    <div class="AssetElement__Body">
        <CharInputWrapping
            v-if="isTitleInEdition"
            v-model="titleEdited"
            class="nameEditionInput my-2 p-2"
            ref="titleEditionInput"
            @focusout="endTitleEdition"
            @keyup.enter="endTitleEdition"
        />

        <div
            v-else
            class="AssetElement__Title EditInline"
            @click="startTitleEdition"
        >
            {{ asset.name }}
        </div>

        <div
            v-show="asset.id"
            class="AssetElement__Actions"
        >
            <div
                v-if="asset.is_assembly_executing"
                class="AssetPreview__assemblyExecuting"
            >
                {{ $t("assemblyExecuting") }}
                <br />
                {{ $t("waitBeforeInserting") }}
            </div>

            <div
                v-if="unlinkRequested"
                class="AssetElement__Actions__Message"
            >
                <p>{{ $t("confirmUnlinkMessage") }}</p>
                <a
                    class="button alert"
                    :disabled="$store.state.loading.loadingInProgress.unlinkAsset"
                    :title="$t('confirmUnlink')"
                    @click="unlinkAsset(asset)"
                >
                    {{ $t("confirmUnlink") }}
                </a>
                <a
                    class="button tertiary"
                    @click="unlinkRequested = false"
                >
                    {{ $t("cancel") }}
                </a>
            </div>

            <div
                v-else-if="deletionRequested"
                class="AssetElement__Actions__Message"
            >
                <p>{{ $t("confirmDeletionMessage") }}</p>

                <a
                    class="button alert"
                    :disabled="$store.state.loading.loadingInProgress.deleteAsset"
                    @click="deleteAsset(asset)"
                >
                    <Loading name="deleteAsset" />
                    {{ $t("confirmDeletion") }}
                </a>
                <a
                    class="button tertiary"
                    @click="deletionRequested = false"
                >
                    {{ $t("cancel") }}
                </a>
            </div>

            <template v-else>
                <SmartLink
                    class="button is-xsmall px-2 mb-1"
                    :to="asset.url"
                >
                    {{ $t("details") }}
                </SmartLink>

                <a
                    v-if="asset.is_file_asset"
                    class="button is-xsmall px-2 mb-1"
                    :href="asset.file_url"
                    :title="asset.title"
                >
                    {{ $t("download") }}
                </a>
                <a
                    v-else
                    class="button is-xsmall px-2 mb-1 break-all whitespace-normal inline-block h-auto"
                    :href="asset.file_url"
                    target="_blank"
                    :title="asset.file_url"
                >
                    {{ asset.file_url }}
                </a>

                <a
                    v-if="asset.in_media_library"
                    class="button is-xsmall px-2 mb-1"
                    @click="unlinkRequested = true"
                >
                    {{ $t("unlink") }}
                </a>

                <a
                    v-else
                    class="button is-xsmall px-2 mb-1"
                    @click.prevent="deletionRequested = true"
                >
                    {{ $t("delete") }}
                </a>

                <Popper triggerElementName="PopperRef">
                    <template #triggerElement>
                        <a
                            class="button is-xsmall px-2"
                            ref="PopperRef"
                        >
                            {{ $t("options") }}
                            <!-- The empty span is required to correctly align with flex display -->
                            <span>
                                <Icon
                                    class="caret"
                                    name="ChevronDown"
                                />
                            </span>
                        </a>
                    </template>

                    <template #content>
                        <label class="menu-item">
                            <ToggleButton
                                class="toggle"
                                :labels="true"
                                :value="asset.in_media_library"
                                @change="toggleMediaLibrary"
                            />
                            {{ $t("inMediaLibrary") }}
                        </label>
                    </template>
                </Popper>
            </template>
        </div>

        <div class="absolute bottom-0 right-0 mb-1 mr-1">
            <Loadarium :name="'partialUpdateAsset' + asset.id" />
        </div>
    </div>
</div>
</template>

<script>
import $ from "jquery"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import LinkedAssetsStoreMapper from "./LinkedAssetsStoreMapper"
import PilotMixin from "@components/PilotMixin"
import AssetConverter from "@js/AssetConverter"

import { ToggleButton } from "vue-js-toggle-button"
import AssetPreview from "../AssetPreview.vue"
import CharInputWrapping from "@components/forms/widgets/CharInputWrapping"

export default {
    name: "LinkedAssetsElement",
    mixins: [PilotMixin, LinkedAssetsStoreMapper],
    components: {
        AssetPreview,
        ToggleButton,
        CharInputWrapping,
    },
    props: {
        asset: Object,
        gridView: {
            type: Boolean,
            default: true,
        },
    },
    data: () => ({
        unlinkRequested: false,
        deletionRequested: false,
        isTitleInEdition: false,
        titleEdited: null,
        inMediaLibrary: true,
        assetConverter: new AssetConverter(),
    }),
    computed: {
        mediaLibraryToggleLabels() {
            return {
                checked: "inMediaLibrary",
                unchecked: "outtaMediaLibrary",
            }
        },
    },
    methods: {
        startTitleEdition() {
            this.titleEdited = this.asset.title
            this.isTitleInEdition = true
            this.$nextTick(() => {
                $(this.$refs.titleEditionInput.$el).focus()
            })
        },
        endTitleEdition() {
            this.partialUpdateAsset({
                id: this.asset.id,
                title: this.titleEdited,
            }).then(() => (this.isTitleInEdition = false))
        },
        toggleMediaLibrary() {
            this.partialUpdateAsset({
                id: this.asset.id,
                in_media_library: !this.asset.in_media_library,
            })
        },
    },
    created() {
        // If an assembly is executing, start to poll for the conversion status
        if (this.asset.is_assembly_executing) {
            this.assetConverter.waitForAssetConversionStatus(this.asset)
        }

        this.assetConverter.on("conversionStatusUpdate", (asset) => {
            this.updateLinkedAsset(asset)
        })
    },
    i18n: {
        messages: {
            fr: {
                assemblyExecuting: "Upload terminé, calcul de l'aperçu",
                confirmDeletionMessage:
                    "Ce fichier est exclusivement lié à ce contenu. Il sera supprimé.",
                confirmUnlink: "Confirmer détacher",
                confirmUnlinkMessage:
                    "Souhaitez vous détacher ce fichier ? (il restera disponible dans la médiathèque)",
                download: "Télécharger",
                inMediaLibrary: "Dans la mediathèque",
                unlink: "Détacher",
                waitBeforeInserting:
                    "Veuillez attendre la fin avant d'insérer l'image dans le contenu",
            },
            en: {
                assemblyExecuting: "Upload ok, calculating preview",
                confirmDeletionMessage:
                    "This file is exclusively linked to this content. It will be deleted.",
                confirmUnlink: "Confirm unlink",
                confirmUnlinkMessage:
                    "Do you want to unlink this file ? (it will still be available in the media library)",
                download: "Download",
                inMediaLibrary: "In media library",
                unlink: "Unlink",
                waitBeforeInserting:
                    "Please wait completion before inserting the image in the content",
            },
        },
    },
}
</script>
