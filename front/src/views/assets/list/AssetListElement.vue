<template>
<div class="AssetElement">
    <AssetPreview
        :asset="asset"
        context="list"
    />

    <div class="AssetElement__Body">
        <SmartLink
            class="AssetElement__Title"
            :to="asset.url"
        >
            {{ asset.name }}
        </SmartLink>

        <div v-if="asset.folder">
            <Label
                class="text-xs rounded"
                :goToListOnClick="true"
                :label="asset.folder"
            />
        </div>

        <div class="text-gray-500 text-small">
            {{ asset.extension }}&nbsp;&bullet;&nbsp;{{ asset.readable_file_size }}
            <span
                v-if="asset.is_assembly_executing"
                class="AssetPreview__assemblyExecuting ml-4"
            >
                {{ $t("assemblyExecuting") }}
            </span>
        </div>
    </div>

    <div v-if="context == 'picker'">
        <a
            v-if="isAssetLinked(asset.id)"
            class="button disabled"
        >
            {{ $t("assetAlreadyLinked") }}
        </a>
        <SmartButtonSpinner
            v-else
            :name="`linkAsset-${asset.id}`"
            :timeout="0"
            @click="$emit('link', asset)"
        >
            {{ $t("linkAsset") }}
        </SmartButtonSpinner>
    </div>
</div>
</template>

<script>
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import PilotMixin from "@components/PilotMixin"
import AssetConverter from "@js/AssetConverter"

import AssetPreview from "../AssetPreview.vue"
import Label from "@views/labels/Label.vue"

export default {
    name: "AssetListElement",
    mixins: [PilotMixin],
    components: {
        AssetPreview,
        Label,
    },
    props: {
        // Can be "list" or "picker"
        context: String,
        asset: {
            type: Object,
            required: true,
        },
        isAssetLinked: {
            type: Function,
            default: () => false,
        },
    },
    data: () => ({
        assetConverter: new AssetConverter(),
    }),
    methods: {
        ...mapMutations("assetList", ["updateAsset"]),
    },
    created() {
        // If an assembly is executing, start to poll for the conversion status
        if (this.asset.is_assembly_executing) {
            this.assetConverter.waitForAssetConversionStatus(this.asset)
        }

        this.assetConverter.on("conversionStatusUpdate", (asset) => {
            this.updateAsset(asset)
        })
    },
    i18n: {
        messages: {
            fr: {
                assetAlreadyLinked: "Fichier déjà lié",
                creation: "Date de création",
                fileType: "Type de fichier",
                linkAsset: "Lier ce fichier",
            },
            en: {
                assetAlreadyLinked: "Asset already linked",
                creation: "Created at",
                fileType: "File type",
                linkAsset: "Link asset",
            },
        },
    },
}
</script>
