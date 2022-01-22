<template>
<div class="bg-white overflow-hidden rounded border border-gray-200 p-6 mb-5">
    <BarLoader
        :color="colors.grey500"
        :loading="!projel.id"
        :width="100"
        widthUnit="%"
    />

    <template v-if="projel.id">
        <div class="flex justify-between items-center font-bold text-gray-800 text-base h-10">
            <div class="text-lg font-bold">
                {{ $t("description") }}
            </div>
            <div
                v-if="!descriptionHtml && !isDescriptionInEdition"
                class="text-gray-500 font-normal"
            >
                {{ $t(isChannelRoute ? "noChannelDescription" : "noProjelDescription") }}
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
import { mapState, mapGetters, mapActions } from "vuex"
import PilotMixin from "@components/PilotMixin"
import { richTextSchema } from "@richText/schema"

export default {
    name: "ProjelDetailDescription",
    mixins: [PilotMixin],
    data: () => ({
        isDescriptionInEdition: false,
        descriptionEdited: {},
    }),
    computed: {
        ...mapState("projelDetail", ["projel", "fieldsCurrentlyUpdating"]),
        ...mapGetters("projelDetail", ["projelId", "isChannelRoute", "isProjectRoute"]),
        descriptionHtml() {
            return richTextSchema.HTMLFromJSON(this.projel.description)
        },
    },
    methods: {
        ...mapActions("projelDetail", ["partialUpdateProjel"]),
        startDescriptionEdition() {
            this.descriptionEdited = this.projel.description
            this.isDescriptionInEdition = true
        },
        cancelDescriptionEdition() {
            this.descriptionEdited = {}
            this.isDescriptionInEdition = false
        },
        endDescriptionEdition() {
            this.partialUpdateProjel({
                description: this.descriptionEdited,
            }).then(() => (this.isDescriptionInEdition = false))
        },
    },
    i18n: {
        messages: {
            fr: {
                noChannelDescription: "Le canal n'a pas de description",
                noProjelDescription: "Le projet n'a pas de description",
            },
            en: {
                noChannelDescription: "The channel has no description yet",
                noProjelDescription: "The project has no description yet",
            },
        },
    },
}
</script>
