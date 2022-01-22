<template>
<Fragment>
    <Popper
        closeOnClickSelector=".willClose"
        triggerElementName="PopperRef"
        triggerType="click"
    >
        <template #triggerElement>
            <button
                class="button is-topbar"
                ref="PopperRef"
            >
                {{ $t("actions") }}
                <!-- The empty span is required to correctly align with flex display -->
                <span>
                    <Icon
                        class="caret"
                        name="ChevronDown"
                    />
                </span>
            </button>
        </template>

        <template #content>
            <AssetDetailOptions />
        </template>
    </Popper>

    <a
        class="button is-blue"
        :href="asset.file_url"
    >
        <!-- The empty span is required to correctly align with flex display -->
        <span>
            <Icon
                class="text-white"
                name="Download"
            />
        </span>
        <span>{{ $t("downloadOriginal", { size: humanFileSize(asset.size) }) }}</span>
    </a>
</Fragment>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"
import { humanFileSize } from "@js/localize.js"
import { Fragment } from "vue-fragment"

import AssetDetailOptions from "./AssetDetailOptions"

export default {
    name: "AssetDetailTopBarActions",
    mixins: [PilotMixin],
    components: {
        Fragment,
        AssetDetailOptions,
    },
    data: () => ({
        humanFileSize,
    }),
    computed: {
        ...mapState("assetDetail", ["asset"]),
    },
    i18n: {
        messages: {
            fr: {
                downloadOriginal: "Télécharger l'original ({size})",
            },
            en: {
                downloadOriginal: "Download the original ({size})",
            },
        },
    },
}
</script>
