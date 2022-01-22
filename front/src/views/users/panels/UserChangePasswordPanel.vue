<template>
<OffPanel name="UserChangePasswordPanel">
    <div slot="offPanelTitle">{{ $t("changePassword") }}</div>
    <div slot="offPanelBody">
        {{ $t("changePasswordIntro") }}

        <AutoForm
            :callToActionText="$t('changePassword')"
            :saveUrl="urls.usersMeChangePassword"
            :schema="changePasswordFormSchema"
            :successText="$t('passwordChangedConfirmation')"
            @cancel="closeOffPanel('UserChangePasswordPanel')"
            @saved="onPasswordChanged"
        />
    </div>
</OffPanel>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "UserChangePasswordPanel",
    mixins: [PilotMixin],
    computed: {
        changePasswordFormSchema() {
            return [
                {
                    name: "old_password",
                    type: "password",
                    label: this.$t("old_password"),
                    required: true,
                },
                {
                    name: "new_password1",
                    type: "password",
                    label: this.$t("new_password1"),
                    required: true,
                },
                {
                    name: "new_password2",
                    type: "password",
                    label: this.$t("new_password2"),
                    required: true,
                },
            ]
        },
    },
    methods: {
        ...mapMutations("offPanel", ["closeOffPanel"]),
        onPasswordChanged() {
            setTimeout(() => this.closeOffPanel("UserChangePasswordPanel"), 2000)
        },
    },
    i18n: {
        messages: {
            fr: {
                changePassword: "Modifier le mot de passe",
                changePasswordIntro:
                    "Entrez votre ancien mot de passe par mesure de sécurité puis entrez le nouveau mot de passe deux fois afin que nous puissions vérifier qu'il est écrit correctement.",
                new_password1: "Nouveau mot de passe",
                new_password2: "Nouveau mot de passe (encore)",
                old_password: "Ancien mot de passe",
                passwordChangedConfirmation: "Mot de passe modifié avec succès.",
            },
            en: {
                changePassword: "Change password",
                changePasswordIntro: "Please type in your old password then your new one twice.",
                new_password1: "New password",
                new_password2: "New password (again)",
                old_password: "Old password",
                passwordChangedConfirmation: "Password successfully changed.",
            },
        },
    },
}
</script>
