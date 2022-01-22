<template>
<div class="mx-auto rounded bg-white shadow p-5 m-10 w-full sm:max-w-lg">
    <Loadarium name="fetchInvitationContext">
        <div class="flex items-center justify-between mb-5">
            <div class="font-black text-xl">
                <template v-if="invitationContext.invalid_token">
                    {{ $t("invalidToken.heading") }}
                </template>
                <template v-else-if="invitationContext.used_token">
                    {{ $t("usedToken.heading") }}
                </template>
                <template
                    v-else-if="
                        invitationContext.different_user_connected && !isSeparateUserConfirmed
                    "
                >
                    {{ $t("differentUserConnected.heading") }}
                </template>
                <template v-else>
                    {{ $t("joinDesk.heading") }}
                </template>
            </div>
            <LanguageSwitcher />
        </div>

        <template v-if="invitationContext.invalid_token">
            {{ $t("invalidToken.content") }}
        </template>

        <template v-else-if="invitationContext.used_token">
            {{ $t("usedToken.content") }}
        </template>

        <template
            v-else-if="invitationContext.different_user_connected && !isSeparateUserConfirmed"
        >
            <div v-html="$t('differentUserConnected.content', invitationContext)" />

            <button
                class="button is-orange expanded"
                @click="isSeparateUserConfirmed = true"
            >
                {{ $t("differentUserConnected.confirm") }}
            </button>
        </template>

        <template v-else>
            <div
                v-html="$t('joinDesk.synthesisPanel', invitationContext)"
                class="bg-blue-100 rounded p-2 py-3 my-4"
            />

            <BaseForm
                autocomplete="off"
                :callToActionText="$t('invitationConfirmCTA')"
                :model="model"
                :saveUrl="urls.authInvitationConfirm"
                :showCancel="false"
                :vuelidate="invitationContext.existing_user_name ? null : $v.model"
                @saved="onSaved"
            >
                <div
                    v-if="invitationContext.existing_user_name"
                    v-html="$t('joinDesk.existingUser', invitationContext)"
                />

                <template v-else>
                    <div class="text-lg font-bold my-3">{{ $t("createYourPassword") }}</div>

                    <FormField
                        v-model="model.password1"
                        :schema="{
                            type: 'password',
                            label: $t('form.password1'),
                        }"
                        :vuelidate="$v.model.password1"
                    />

                    <FormField
                        v-model="model.password2"
                        :schema="{
                            type: 'password',
                            label: $t('form.password2'),
                        }"
                        :vuelidate="$v.model.password2"
                    />

                    <div class="flex items-center">
                        <input
                            v-model="model.terms_acceptance"
                            class="mr-5"
                            type="checkbox"
                        />
                        <span v-html="$t('form.termsAcceptance')" />
                    </div>
                    <ValidationErrors :validation="$v.model.terms_acceptance" />
                </template>
            </BaseForm>
        </template>
    </Loadarium>
</div>
</template>

<script>
import { required } from "vuelidate/lib/validators"
import { $httpX } from "@js/ajax.js"
import PilotMixin from "@components/PilotMixin"

import LanguageSwitcher from "@components/LanguageSwitcher.vue"

export default {
    name: "InvitationConfirm",
    mixins: [PilotMixin],
    components: {
        LanguageSwitcher,
    },
    data: () => ({
        invitationContext: {},
        model: {
            password1: "",
            password2: "",
            terms_acceptance: false,
            token: "",
        },
        isSeparateUserConfirmed: false,
    }),
    validations: {
        model: {
            password1: { required },
            password2: { required },
            terms_acceptance: {},
        },
    },
    methods: {
        onSaved() {
            window.location = "/"
        },
    },
    created() {
        this.model.token = this.$router.currentRoute.params.token

        $httpX({
            name: "fetchInvitationContext",
            commit: this.$store.commit,
            url: this.urls.authInvitationConfirm,
            method: "GET",
            params: {
                token: this.$router.currentRoute.params.token,
            },
        }).then((response) => {
            this.invitationContext = response.data
        })
    },
    i18n: {
        messages: {
            fr: {
                createYourPassword: "Créez votre mot de passe",
                invitationConfirmCTA: "Rejoindre le desk",
                invalidToken: {
                    heading: "Lien invalide",
                    content: "Ce lien d'invitation n'est pas correct.",
                },
                usedToken: {
                    heading: "Lien invalide",
                    content: "Ce lien d'invitation n'est plus valable car il a déjà été utilisé.",
                },
                differentUserConnected: {
                    heading: "!! Attention !!",
                    content: `
                        <p>Vous êtes actuellement connecté à Pilot avec l'email <b>{current_email}</b></p>
                        <p>Vous avez été invité sur sur le desk <b>{desk_name}</b> avec une autre adresse email <b>{invitation_email}</b></p>
                        <p>
                            Si vous validez cette invitation, vous aurez deux comptes différent sur Pilot.
                            Vous ne pourrez alors pas profiter de la fonctionnalité de bascule rapide entre desks.
                        </p>
                        <p>Pour utiliser un seul compte, vous pouvez demander une nouvelle invitation à <b>{inviter}</b> sur votre autre adresse email {current_email}.</p>
                        <p>Si cependant vous souhaitez continuer avec deux comptes séparés, cliquez sur le bouton ci-dessous.</p>
                    `,
                    confirm: "Oui je veux utiliser un autre compte",
                },
                joinDesk: {
                    heading: "Confirmez votre invitation",
                    synthesisPanel: `
                        <p>Vous avez été invité par <b>{inviter}</b></p>
                        <p>Vous rejoignez le desk <b>{desk_name}</b></p>
                        <p>Votre E-mail est <b>{invitation_email}</b></p>
                    `,
                    existingUser: `
                        <p>Vous avez déjà un compte sur Pilot : <b>{existing_user_name}</b>.</p>
                        <p>Ce compte sera associé au desk {desk_name}</p>
                    `,
                },
                form: {
                    password1: "Mot de passe",
                    password2: "Confirmer le mot de passe",
                    termsAcceptance:
                        "J'accepte les <a href='https://www.pilot.pm/fr/policies/terms/' target='_blank'>Conditions Générales d'Utilisation</a>",
                },
            },
            en: {
                createYourPassword: "Create your password",
                invitationConfirmCTA: "Join the desk",
                invalidToken: {
                    heading: "Invalid link",
                    content: "This activation link is incorrect.",
                },
                usedToken: {
                    heading: "Invalid link",
                    content: "This invitation link is invalid because it has already been used.",
                },
                differentUserConnected: {
                    heading: "!! Warning !!",
                    content: `
                        <p>You are currently connected to Pilot with the account <b>{current_email}</b></p>
                        <p>You have been invited to the desk <b>{desk_name}</b> through another email address <b>{invitation_email}</b></p>
                        <p>
                            If you confirm this invitation, you will end up with two separate accounts on Pilot.
                            You'll then be unable to enjoy the quick desk switching feature.
                        </p>
                        <p>To use a single account, you can ask for a new invitation to <b>{inviter}</b> through you other email address {current_email}.</p>
                        <p>If however you want to go ahead with two separate accounts, please click on the button below.</p>
                    `,
                    confirm: "Yes I want to use another account",
                },
                joinDesk: {
                    heading: "Confirm your invitation",
                    synthesisPanel: `
                        <p>You've been invited by <b>{inviter}</b></p>
                        <p>You join the desk <b>{desk_name}</b></p>
                        <p>Your E-mail is <b>{invitation_email}</b></p>
                    `,
                    existingUser: `
                        <p>You already have a Pilot account : <b>{existing_user_name}</b>.</p>
                        <p>This account will be associated to the desk {desk_name}</p>
                    `,
                },
                form: {
                    password1: "Password",
                    password2: "Confirm the password",
                    termsAcceptance:
                        "I accept the <a href='https://www.pilot.pm/policies/terms/' target='_blank'>Terms of Service</a>",
                },
            },
        },
    },
}
</script>
