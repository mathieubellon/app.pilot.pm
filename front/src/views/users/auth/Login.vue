<template>
<div class="rounded bg-white shadow mx-auto p-5 m-10 w-full max-w-lg">
    <div class="flex items-center justify-between mb-5">
        <div class="font-black text-xl">{{ $t("login") }}</div>
        <LanguageSwitcher />
    </div>

    <BaseForm
        autocomplete="off"
        :callToActionText="$t('login')"
        :model="model"
        :resetTimeout="999999"
        :saveUrl="urls.authLogin"
        :showCancel="false"
        :vuelidate="$v.model"
        @saved="onLoggedIn"
    >
        <div class="form__field">
            <label>
                <div class="form__field__label">{{ $t("emailAdress") }}</div>
                <input
                    v-model="model.username"
                    autocapitalize="none"
                    autocorrect="off"
                    autofocus
                    placeholder="myemail@emailhost.com"
                    required
                    type="email"
                />
            </label>
            <ValidationErrors :validation="$v.model.username" />
        </div>

        <div class="form__field">
            <label>
                <div class="form__field__label">{{ $t("password") }}</div>
                <input
                    v-model="model.password"
                    required
                    type="password"
                />
            </label>
            <ValidationErrors :validation="$v.model.password" />
            <SmartLink
                class="text-xs text-gray-600 underline"
                :to="{
                    name: 'passwordReset',
                    params: model.username ? { email: model.username } : {},
                }"
            >
                {{ $t("passwordForgotten") }}
            </SmartLink>
        </div>

        <label class="flex">
            <input
                v-model="model.remember_me"
                class="m-1"
                type="checkbox"
            />
            <div class="flex flex-col mx-2">
                <div class="text-sm font-semibold leading-tight">{{ $t("rememberMe") }}</div>
                <div class="text-xs text-gray-500">{{ $t("possibleCorporateRestrictions") }}</div>
            </div>
        </label>
    </BaseForm>

    <div class="flex flex-col items-center w-full mt-10">
        <div class="text-sm text-gray-500 font-medium">{{ $t("notRegisteredYet") }}</div>
        <div>
            <SmartLink
                class="text-sm"
                to="/registration/"
            >
                {{ $t("createAccount") }}
            </SmartLink>
        </div>
    </div>
</div>
</template>

<script>
import { parseQueryString } from "@js/queryString"
import { required } from "vuelidate/lib/validators"
import PilotMixin from "@components/PilotMixin"

import LanguageSwitcher from "@components/LanguageSwitcher.vue"

let queryParams = parseQueryString(document.location.search)

export default {
    name: "Login",
    mixins: [PilotMixin],
    components: {
        LanguageSwitcher,
    },
    data: () => ({
        model: {
            username: "",
            password: "",
            remember_me: false,
            next: (queryParams.next || [])[0],
        },
    }),
    validations: {
        model: {
            username: { required },
            password: { required },
        },
    },
    methods: {
        onLoggedIn({ redirect }) {
            window.location = redirect
        },
    },
    i18n: {
        messages: {
            fr: {
                createAccount: "Créer un compte",
                login: "Connexion",
                notRegisteredYet: "Pas encore inscrit ?",
                passwordForgotten: "J'ai oublié mon mot de passe",
                rememberMe: "Se souvenir de moi",
                possibleCorporateRestrictions: "Fonctionne si votre réseau d'entreprise l'autorise",
            },
            en: {
                createAccount: "Sign up",
                login: "Login",
                notRegisteredYet: "Not registered yet?",
                passwordForgotten: "I have forgotten my password",
                rememberMe: "Remember me",
                possibleCorporateRestrictions: "Works if your corporate network allows it",
            },
        },
    },
}
</script>
