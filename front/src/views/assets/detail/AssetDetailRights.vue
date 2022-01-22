<template>
<div class="AssetDetailRights">
    <div class="bg-white border border-gray-200 rounded p-4">
        <a
            class="button is-blue mb-4"
            @click="addAssetRight"
        >
            {{ $t("addAssetRight") }}
        </a>

        <div v-if="!asset.asset_rights || asset.asset_rights.length == 0">
            <div class="help-text">
                <div class="help-text-title">{{ $t("noAssetRightYet") }}</div>
                <div class="help-text-content">{{ $t("explainAssetRight") }}</div>
            </div>
        </div>
        <div class="flex flex-wrap">
            <AssetDetailRightElement
                v-for="assetRight in sortedAssetRight"
                :assetRight="assetRight"
                :key="assetRight.id"
                @editAssetRight="editAssetRight(assetRight)"
            />
        </div>
    </div>

    <OffPanel name="assetRightForm">
        <div slot="offPanelTitle">{{ $t("assetRight") }}</div>
        <div slot="offPanelBody">
            <AssetRightForm
                :assetId="asset.id"
                :assetRight="assetRightInForm"
                @saved="onAssetRightSaved"
            />
        </div>
    </OffPanel>
</div>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import AssetRightForm from "./AssetRightForm.vue"
import AssetDetailRightElement from "./AssetDetailRightElement"

export default {
    name: "AssetDetailRights",
    mixins: [PilotMixin],
    components: {
        AssetRightForm,
        AssetDetailRightElement,
    },
    data: () => ({
        assetRightInForm: {},
    }),
    computed: {
        ...mapState("assetDetail", ["asset"]),
        sortedAssetRight() {
            return _.sortBy(this.asset.asset_rights, "expiry")
        },
    },
    methods: {
        addAssetRight() {
            this.assetRightInForm = {}
            this.openOffPanel("assetRightForm")
        },
        editAssetRight(assetRight) {
            this.assetRightInForm = assetRight
            this.openOffPanel("assetRightForm")
        },
        onAssetRightSaved(assetRight) {
            // Edition
            if (this.assetRightInForm.id) {
                _.assign(this.assetRightInForm, assetRight)
            }
            // Creation
            else {
                this.asset.asset_rights.push(assetRight)
            }
            this.closeOffPanel("assetRightForm")
        },
    },
    i18n: {
        messages: {
            fr: {
                addAssetRight: "Ajouter un droit d'utilisation",
                explainAssetRight:
                    "Vous pouvez renseigner les droits d'utilisation du fichier, avec une notification à la date d'expiration",
                noAssetRightYet: "Aucun droit d'utilisation",
            },
            en: {
                addAssetRight: "Add usage right",
                explainAssetRight:
                    "You can store the usage rights of the media, with a notification at the expiry date",
                noAssetRightYet: "No usage right",
            },
        },
    },
}
</script>
