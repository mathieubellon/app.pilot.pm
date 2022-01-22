<template>
<AutoForm
    :initialData="{
        in_media_library: true,
    }"
    :saveUrl="urls.assetsCreateUrlAsset"
    :schema="assetUrlFormSchema"
    :urlParams="{ contentTypeId: contentType.id, objectId }"
    @cancel="hideAssetUrlForm"
    @saved="onUrlAssetSaved"
/>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import LinkedAssetsStoreMapper from "./LinkedAssetsStoreMapper"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "AssetUrlForm",
    mixins: [PilotMixin, LinkedAssetsStoreMapper],
    computed: {
        assetUrlFormSchema() {
            return [
                {
                    name: "url",
                    type: "char",
                    label: this.$t("formUrl"),
                    placeholder: this.$t("formUrl"),
                    required: true,
                },
                {
                    name: "title",
                    type: "char",
                    label: this.$t("formTitle"),
                    placeholder: this.$t("formTitle"),
                    required: true,
                },
                {
                    name: "description",
                    type: "richText",
                    label: this.$t("description"),
                },
            ]
        },
    },
    methods: {
        onUrlAssetSaved(asset) {
            this.prependLinkedAsset(asset)
            this.hideAssetUrlForm()
        },
    },
    i18n: {
        messages: {
            fr: {
                defaultLinked:
                    "Par défaut le fichier est uniquement lié à ce contenu.<br>Cochez cette case si vous souhaitez le rendre disponible dans la médiathèque",
                formUrl: "Lien externe",
                formTitle: "Nom",
                description: "Description",
            },
            en: {
                defaultLinked:
                    "By default the file is only linked to this content. Check this box if you want to make it available in the media library",
                formUrl: "External link",
                formTitle: "Name",
                description: "Description",
            },
        },
    },
}
</script>
