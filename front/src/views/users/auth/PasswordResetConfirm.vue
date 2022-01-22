<template>
<div class="mx-auto rounded bg-white shadow p-5 m-10 w-full sm:max-w-lg">
    <div class="flex items-center justify-between mb-5">
        <div class="font-black text-xl">{{ $t("newPassword") }}</div>
        <LanguageSwitcher />
    </div>
    <template v-if="invalidToken">
        {{ $t("invalidToken") }}
    </template>

    <template v-else-if="!isFormSent">
        <div class="my-5">{{ $t("introText") }}</div>

        <AutoForm
            autocomplete="off"
            :callToActionText="$t('passwordSetCTA')"
            :initialData="{
                token: authContext.token,
                uidb64: authContext.uidb64,
            }"
            :saveUrl="urls.authPasswordSet"
            :schema="passwordResetConfirmFormSchema"
            :showCancel="false"
            @saved="onFormSent"
        />
    </template>

    <template v-else>
        <p>{{ $t("passwordResetDone") }}</p>

        <p>{{ $t("passwordHasBeenSaved") }}</p>

        <SmartLink
            class="button is-blue expanded my-4"
            to="/login/"
        >
            {{ $t("login") }}
        </SmartLink>
    </template>
</div>
</template>

<script>
import PilotMixin from "@components/PilotMixin"

import LanguageSwitcher from "@components/LanguageSwitcher.vue"

export default {
    name: "PasswordResetConfirm",
    mixins: [PilotMixin],
    components: {
        LanguageSwitcher,
    },
    data: () => ({
        authContext: window.authContext,
        invalidToken: window.authContext.invalidToken,
        isFormSent: false,
    }),
    computed: {
        passwordResetConfirmFormSchema() {
            return [
                {
                    type: "password",
                    name: "password1",
                    label: this.$t("password1"),
                    required: true,
                },
                {
                    type: "password",
                    name: "password2",
                    label: this.$t("password2"),
                    required: true,
                },
            ]
        },
    },
    methods: {
        onFormSent() {
            this.isFormSent = true
        },
    },
    i18n: {
        messages: {
            fr: {
                introText:
                    "Merci d'entrer deux fois votre mot de passe pour vérifier qu'il est saisi correctement.",
                invalidToken:
                    "Le lien de réinitialisation était invalide, peut être parce qu'il a déjà été utilisé. veuillez demander à nouveau une réinitialisation du mot de passe.",
                login: "Connexion",
                newPassword: "Nouveau mot de passe",
                passwordHasBeenSaved:
                    "Votre mot de passe a été enregistré. Vous pouvez continuer et vous connecter.",
                passwordResetDone: "✓ Réinitialisation du mot de passe terminée",
                passwordSetCTA: "Modifier mon mot de passe",
                password1: "Mot de passe",
                password2: "Confirmer le mot de passe",
            },
            en: {
                introText:
                    "Thank you to double enter your password to verify it is entered correctly.",
                invalidToken:
                    "The reset link was invalid, maybe because it was already used. please request a password reset again.",
                login: "Login",
                newPassword: "New password",
                passwordHasBeenSaved: "Your password has been saved. You can go ahead and log in.",
                passwordResetDone: "✓ Password reset complete",
                passwordSetCTA: "Reset my password",
                password1: "Password",
                password2: "Confirm the password",
            },
        },
    },
}
</script>
