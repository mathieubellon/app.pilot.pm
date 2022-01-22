<template>
<Loadarium name="fetchDesk">
    <BaseForm
        :disableSave="!validation.deskModel.$anyDirty || $refs.logo.uploadInProgress"
        :model="deskModel"
        :saveUrl="urls.desksCurrent"
        :showCancel="false"
        :vuelidate="validation.deskModel"
        @saved="onDeskSaved"
    >
        <FormField
            :schema="{
                type: 'char',
                label: $t('name'),
                placeholder: $t('name'),
            }"
            v-model.trim="deskModel.name"
            :vuelidate="validation.deskModel.name"
        />

        <FileField
            ref="logo"
            :acceptUrl="urls.desksS3SignatureForLogo"
            :buttonText="$t('uploadLogo')"
            :currentFile="desk.logo"
            :height="50"
            :label="$t('logo')"
            :width="50"
            @input="onLogoInput"
        />
    </BaseForm>
</Loadarium>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"

import PilotMixin from "@components/PilotMixin"

import FileField from "@components/forms/widgets/FileField"

export default {
    name: "DeskEdit",
    mixins: [PilotMixin],
    components: {
        FileField,
    },
    props: {
        deskModel: Object,
        validation: Object,
    },
    computed: {
        ...mapState("desk", ["desk"]),
    },
    methods: {
        ...mapMutations("desk", ["setDesk"]),
        onLogoInput(logo) {
            this.deskModel.logo = logo
            this.validation.deskModel.$touch()
        },
        onDeskSaved(desk) {
            this.setDesk(desk)
            this.$refs.logo.reset()
            this.currentDesk.name = this.desk.name
            this.currentDesk.logoUrl = this.desk.logo
        },
    },
    i18n: {
        messages: {
            fr: {
                logo: "Logo",
                uploadLogo: "Envoyer un logo pour le desk",
            },
            en: {
                logo: "Logo",
                uploadLogo: "Upload logo for your desk",
            },
        },
    },
}
</script>
