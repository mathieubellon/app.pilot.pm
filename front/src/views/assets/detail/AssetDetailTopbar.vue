<template>
<div class="AssetDetailTopbar flex items-end w-full">
    <div class="flex flex-grow truncate">
        <div class="bg-white mr-2 py-0">
            <Icon
                class="text-gray-400 w-5"
                name="Asset"
            />
        </div>

        <Spinner v-if="fieldsCurrentlyUpdating.title" />

        <input
            v-else-if="isTitleInEdition"
            v-model="titleEdited"
            class="nameEditionInput font-bold"
            ref="nameEditionInput"
            @blur="endNameEdition"
            @keyup.enter="endNameEdition"
        />

        <div
            v-else
            class="cursor-pointer truncate"
            @click="setIsTitleInEdition(true)"
        >
            {{ asset.title }}
        </div>
    </div>
</div>
</template>

<script>
import $ from "jquery"
import { mapState, mapMutations, mapActions } from "vuex"

import PilotMixin from "@components/PilotMixin"

export default {
    name: "AssetDetailTopbar",
    mixins: [PilotMixin],
    data: () => ({
        titleEdited: "",
    }),
    computed: {
        ...mapState("assetDetail", ["asset", "fieldsCurrentlyUpdating", "isTitleInEdition"]),
    },
    watch: {
        isTitleInEdition() {
            if (this.isTitleInEdition) {
                this.startNameEdition()
            }
        },
    },
    methods: {
        ...mapMutations("assetDetail", ["setIsTitleInEdition"]),
        ...mapActions("assetDetail", ["partialUpdateAsset"]),
        startNameEdition() {
            this.titleEdited = this.asset.title
            this.$nextTick(() => {
                $(this.$refs.nameEditionInput).focus()
            })
        },
        endNameEdition() {
            this.partialUpdateAsset({
                title: this.titleEdited,
            }).then(() => this.setIsTitleInEdition(false))
        },
    },
}
</script>
