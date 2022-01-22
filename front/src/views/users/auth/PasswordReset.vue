<template>
<div class="mx-auto rounded bg-white shadow p-5 m-10 w-full sm:max-w-lg">
    <div class="flex items-center justify-between mb-5">
        <div class="font-black text-xl">{{ $t("passwordReset") }}</div>
        <LanguageSwitcher />
    </div>

    <template v-if="!isFormSent">
        <div class="my-5">{{ $t("introText") }}</div>

        <AutoForm
            autocomplete="off"
            :callToActionText="$t('passwordResetCTA')"
            :initialData="{
                email: $route.params.email,
            }"
            :saveUrl="urls.authPasswordReset"
            :schema="passwordResetFormSchema"
            :showCancel="false"
            @saved="onFormSent"
        />
    </template>

    <template v-else>
        <div class="text-green-500 mb-5 font-semibold">{{ $t("formSent") }}</div>

        <div>{{ $t("emailMaybeSent") }}</div>

        <div>{{ $t("emailShouldArrive") }}</div>
    </template>

    <SmartLink
        class="button w-full my-4"
        to="/login/"
    >
        {{ $t("backToLogin") }}
    </SmartLink>
</div>
</template>

<script>
import PilotMixin from "@components/PilotMixin"
import LanguageSwitcher from "@components/LanguageSwitcher.vue"

export default {
    name: "PasswordReset",
    mixins: [PilotMixin],
    components: {
        LanguageSwitcher,
    },
    data: () => ({
        isFormSent: false,
    }),
    computed: {
        passwordResetFormSchema() {
            return [
                {
                    type: "email",
                    name: "email",
                    label: this.$t("emailAdress"),
                    placeholder: "john@doe.com",
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
                backToLogin: "Retour",
                emailShouldArrive:
                    "Vous devriez le recevoir rapidement. Dans le cas contraire, l'adresse entrée était peut-être incorrecte.",
                emailMaybeSent:
                    "Si l'adresse indiquée correspond à un utilisateur, nous avons envoyé un email contenant les informations de réinitialisation du mot de passe.",
                formSent: "✓ Instructions envoyées",
                introText:
                    "Saisissez votre email, nous vous enverrons les instructions pour le réinitialiser.",
                passwordReset: "Réinitialisation du mot de passe",
                passwordResetCTA: "Réinitialiser mon mot de passe",
            },
            en: {
                backToLogin: "Back to login",
                emailShouldArrive:
                    "You should receive it quickly. Otherwise, the entered address may have been incorrect.",
                emailMaybeSent:
                    "If the specified address matches a user, we sent an email containing the password reset information.",
                formSent: "✓ Instructions sent",
                introText: "Enter your email, we will send you instructions to reset it.",
                passwordReset: "Reset password",
                passwordResetCTA: "Reset my password",
            },
        },
    },
}
</script>
