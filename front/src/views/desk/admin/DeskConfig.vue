<template>
<Loadarium :name="['fetchDesk', 'fetchLanguages']">
    <BaseForm
        :model="deskModel"
        :saveUrl="urls.desksCurrent"
        :showCancel="false"
        @saved="onDeskSaved"
    >
        <FormField
            v-model="deskModel.private_items_enabled"
            :schema="{
                type: 'toggle',
                label: this.$t('privateItemsEnabled'),
                help_text: this.$t('privateItemsEnabledHelp'),
            }"
        />

        <FormField
            v-model="deskModel.creation_forms_fields_visibles_by_default"
            :schema="{
                type: 'toggle',
                label: this.$t('creationFormsFieldsVisiblesByDefault'),
                help_text: this.$t('creationFormsFieldsVisiblesByDefaultHelp'),
            }"
        />

        <FormField
            v-model="deskModel.item_languages_enabled"
            :schema="{
                type: 'toggle',
                label: this.$t('itemLanguagesEnabled'),
                help_text: this.$t('itemLanguagesEnabledHelp'),
            }"
        />

        <FormField
            v-if="deskModel.item_languages_enabled"
            v-model="deskModel.allowed_languages"
            :schema="{
                type: 'choice',
                label: this.$t('allowedLanguages'),
                choices: availableLanguages,
                multiple: true,
            }"
        />
    </BaseForm>
</Loadarium>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "DeskConfig",
    mixins: [PilotMixin],
    props: {
        deskModel: Object,
    },
    computed: {
        ...mapState("desk", ["desk", "availableLanguages"]),
    },
    methods: {
        ...mapMutations("desk", ["setDesk"]),
        onDeskSaved(desk) {
            this.setDesk(desk)
        },
    },
    i18n: {
        messages: {
            fr: {
                allowedLanguages: "Langues autorisées pour marquer les contenus",
                creationFormsFieldsVisiblesByDefault:
                    "Afficher par défaut tous les champs des formulaires de créations",
                creationFormsFieldsVisiblesByDefaultHelp:
                    "Si vous cochez cette case, les champs habituellement masqués des formulaires de création seront visibles immédiatement",
                itemLanguagesEnabled: "Langues de contenus activées",
                itemLanguagesEnabledHelp:
                    "Indique si les utilisateurs du desk peuvent indiquer une langue pour les contenus",
                privateItemsEnabled: "Items privés activés",
                privateItemsEnabledHelp:
                    "Indique si les utilisateurs du desk peuvent rendre un item privé",
            },
            en: {
                allowedLanguages: "Languages permitted to mark the content",
                creationFormsFieldsVisiblesByDefault:
                    "Show by default all the fields in creation forms",
                creationFormsFieldsVisiblesByDefaultHelp:
                    "If you check this box, the fields usually hidden in the creation forms will be immediatly visibles",
                itemLanguagesEnabled: "Language mode activated",
                itemLanguagesEnabledHelp: "Indicates whether users can mark content with language",
                privateItemsEnabled: "Set private items activated",
                privateItemsEnabledHelp: "Indicates whether users can mark an item as private",
            },
        },
    },
}
</script>

<style lang="scss"></style>
