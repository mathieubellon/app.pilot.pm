<template>
<div class="mx-auto rounded bg-white shadow p-5 m-10 w-full sm:max-w-lg">
    <div class="flex items-center justify-between mb-5">
        <div class="font-black text-xl">{{ $t("registration") }}</div>
        <LanguageSwitcher />
    </div>

    <template v-if="!isFormSent">
        <BaseForm
            autocomplete="off"
            :callToActionText="$t('registrationCTA')"
            :model="model"
            :saveUrl="urls.authRegistration"
            :showCancel="false"
            :vuelidate="$v.model"
            @saved="onFormSent"
        >
            <FormField
                :schema="{
                    type: 'char',
                    label: $t('organization'),
                    placeholder: $t('orgNamePlaceHolder'),
                }"
                v-model.trim="model.organization"
                :vuelidate="$v.model.organization"
            />

            <FormField
                :schema="{
                    type: 'email',
                    label: $t('emailAdress'),
                    placeholder: 'john@doe.com',
                }"
                v-model.trim="model.email"
                :vuelidate="$v.model.email"
            />

            <FormField
                v-model="model.password1"
                :schema="{
                    type: 'password',
                    label: $t('password1'),
                    help_text: $t('passwordHintPlaceHolder'),
                }"
                :vuelidate="$v.model.password1"
            />

            <FormField
                v-model="model.password2"
                :schema="{
                    type: 'password',
                    label: $t('password2'),
                }"
                :vuelidate="$v.model.password2"
            />

            <div class="flex items-center">
                <input
                    v-model="model.terms_acceptance"
                    class="mr-5"
                    type="checkbox"
                />
                <span v-html="$t('termsAcceptance')" />
            </div>
            <ValidationErrors :validation="$v.model.terms_acceptance" />
        </BaseForm>
    </template>

    <template v-else>
        <p>{{ $t("formSent") }}</p>

        <p>{{ $t("emailShouldArrive") }}</p>
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
import { required, email } from "vuelidate/lib/validators"
import PilotMixin from "@components/PilotMixin"
import LanguageSwitcher from "@components/LanguageSwitcher.vue"

export default {
    name: "Registration",
    mixins: [PilotMixin],
    components: {
        LanguageSwitcher,
    },
    data: () => ({
        isFormSent: false,
        model: {
            email: "",
            organization: "",
            password1: "",
            password2: "",
            terms_acceptance: false,
        },
    }),
    validations: {
        model: {
            email: { required, email },
            organization: { required },
            password1: { required },
            password2: { required },
            terms_acceptance: {},
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
                    "Vous allez recevoir un email de notification à l'adresse email que vous avez renseignée. Veuillez cliquer sur le lien inclus dans l'email afin que nous puissions vérifiez votre adresse email.",
                formSent: "✓ Inscription terminée",
                organization: "Nom de l'espace de travail",
                password1: "Mot de passe",
                password2: "Confirmer le mot de passe",
                registration: "Inscription",
                registrationCTA: "Créer mon espace de travail",
                termsAcceptance:
                    "J'accepte les <a href='https://www.pilot.pm/fr/policies/terms/' target='_blank'>Conditions Générales d'Utilisation</a>",
                orgNamePlaceHolder: "Entreprise team marketing",
                passwordHintPlaceHolder:
                    "Astuce: 'Un grand cheval rouge de 20kg' est aussi sécurisé que Ghh7xà90$$",
            },
            en: {
                backToLogin: "Back to login",
                emailShouldArrive:
                    "You will receive an email notification to the email address you provided. Please click on the link in the email so that we can verify your email address.",
                formSent: "✓ Registration done",
                organization: "Workspace name",
                password1: "Password",
                password2: "Confirm the password",
                registration: "Registration",
                registrationCTA: "Sign up",
                termsAcceptance:
                    "I accept the <a href='https://www.pilot.pm/policies/terms/' target='_blank'>Terms of Service</a>",
                orgNamePlaceHolder: "Entreprise marketing team",
                passwordHintPlaceHolder: "Hint: 'A big 50-pound red horse' is as safe as Ghh7x$90.",
            },
        },
    },
}
</script>
