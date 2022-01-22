<template>
<div class="bg-white overflow-hidden shadow rounded p-6 mb-5">
    <BarLoader
        :color="colors.grey500"
        :loading="!asset.id"
        :width="100"
        widthUnit="%"
    />

    <template v-if="asset.id">
        <div class="flex justify-between items-center font-bold text-gray-800 text-base h-10">
            <div class="text-lg font-bold">
                {{ $t("description") }}
            </div>
            <div
                v-if="!descriptionHtml && !isDescriptionInEdition"
                class="text-gray-500 font-normal"
            >
                {{ $t("noDescription") }}
            </div>

            <div
                v-if="isDescriptionInEdition"
                class="flex"
            >
                <button
                    class="button is-green is-small mr-2"
                    @click="endDescriptionEdition"
                >
                    {{ $t("save") }}
                </button>
                <button
                    class="button is-white is-small"
                    @click="cancelDescriptionEdition"
                >
                    {{ $t("cancel") }}
                </button>
            </div>
            <button
                v-else-if="!descriptionHtml"
                class="button is-blue is-small"
                @click="startDescriptionEdition"
            >
                {{ $t("create") }}
            </button>
            <button
                v-else
                class="button is-small"
                @click="startDescriptionEdition"
            >
                {{ $t("edit") }}
            </button>
        </div>
        <Spinner v-if="fieldsCurrentlyUpdating.description" />
        <RichTextInput
            v-else-if="isDescriptionInEdition"
            v-model="descriptionEdited"
        />
        <div
            v-else-if="descriptionHtml"
            v-html="descriptionHtml"
            class="RichTextStyling"
        />
    </template>
</div>
</template>
<script>
import { mapState, mapActions } from "vuex"
import PilotMixin from "@components/PilotMixin"
import { richTextSchema } from "@richText/schema"

export default {
    name: "AssetDetailDescription",
    mixins: [PilotMixin],
    data: () => ({
        isDescriptionInEdition: false,
        descriptionEdited: {},
    }),
    computed: {
        ...mapState("assetDetail", ["asset", "fieldsCurrentlyUpdating"]),
        descriptionHtml() {
            return richTextSchema.HTMLFromJSON(this.asset.description)
        },
    },
    methods: {
        ...mapActions("assetDetail", ["partialUpdateAsset"]),
        startDescriptionEdition() {
            this.descriptionEdited = this.asset.description
            this.isDescriptionInEdition = true
        },
        cancelDescriptionEdition() {
            this.descriptionEdited = {}
            this.isDescriptionInEdition = false
        },
        endDescriptionEdition() {
            this.partialUpdateAsset({
                description: this.descriptionEdited,
            }).then(() => (this.isDescriptionInEdition = false))
        },
    },
    i18n: {
        messages: {
            fr: {
                noDescription: "Le fichier n'a pas de description",
            },
            en: {
                noDescription: "The asset has no description yet",
            },
        },
    },
}
</script>
