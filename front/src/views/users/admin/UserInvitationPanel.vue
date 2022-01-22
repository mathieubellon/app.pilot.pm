<template>
<OffPanel
    name="UserInvitationPanel"
    @opened="onOpen"
>
    <div slot="offPanelTitle">{{ $t("inviteNewUser") }}</div>
    <div slot="offPanelBody">
        <BaseForm
            :callToActionText="$t('sendInvitation')"
            :errorText="$t('invitationError')"
            :model="userInvitation"
            :saveUrl="urls.usersInvitation"
            :successText="$t('invitationHasBeenSent')"
            :vuelidate="$v.userInvitation"
            @cancel="closeOffPanel('UserInvitationPanel')"
            @saved="onInvitationSent"
        >
            <FormField
                :schema="{
                    type: 'email',
                    label: $t('emailAdress'),
                    placeholder: 'john@doe.com',
                }"
                v-model.trim="userInvitation.email"
                :vuelidate="$v.userInvitation.email"
            />

            <div class="form__field">
                <div class="form__field__label">
                    {{ $t("toWhichUserPermission") }}
                </div>
                <label class="UserInvitationPanel__field__radio">
                    <input
                        v-model="userInvitation.permission"
                        class="UserInvitationPanel__field__radio__input"
                        type="radio"
                        value="Administrators"
                    />
                    <div class="UserInvitationPanel__field__radio__label">
                        <div class="font-semibold">{{ $t("administrator") }}</div>
                        <div class="form__field__help">{{ $t("administrator_description") }}</div>
                    </div>
                </label>
                <label class="UserInvitationPanel__field__radio">
                    <input
                        v-model="userInvitation.permission"
                        class="UserInvitationPanel__field__radio__input"
                        type="radio"
                        value="Editors"
                    />
                    <div class="UserInvitationPanel__field__radio__label">
                        <div class="font-semibold">{{ $t("editor") }}</div>
                        <div class="form__field__help">{{ $t("editor_description") }}</div>
                    </div>
                </label>
                <label class="UserInvitationPanel__field__radio">
                    <input
                        v-model="userInvitation.permission"
                        class="UserInvitationPanel__field__radio__input"
                        type="radio"
                        value="Restricted Editors"
                    />
                    <div class="UserInvitationPanel__field__radio__label">
                        <div class="font-semibold">{{ $t("restricted_editor") }}</div>
                        <div class="form__field__help">
                            {{ $t("restricted_editor_description") }}
                        </div>
                    </div>
                </label>
            </div>
            <div
                v-if="!$v.userInvitation.permission.required"
                class="form__field__error"
            >
                {{ $t("permissionMustBeSelected") }}
            </div>

            <FormField
                :schema="{
                    type: 'choice',
                    label: $t('teams'),
                    choices: teamsChoices,
                    multiple: true,
                }"
                v-model.trim="userInvitation.teams_id"
                :vuelidate="$v.userInvitation.teams_id"
            />
        </BaseForm>
    </div>
</OffPanel>
</template>

<script>
import _ from "lodash"
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"
import { EVENTS, dispatchEvent } from "@js/events"
import { required, email } from "vuelidate/lib/validators"
import PilotMixin from "@components/PilotMixin"

const EMPTY_INVITATION_MODEL = {
    email: "",
    permission: "",
    teams_id: [],
}

export default {
    name: "UserInvitationPanel",
    mixins: [PilotMixin],
    data: () => ({
        userInvitation: _.clone(EMPTY_INVITATION_MODEL),
    }),
    validations: {
        userInvitation: {
            email: { required, email },
            permission: { required },
        },
    },
    computed: {
        ...mapGetters("usersAdmin", ["teamsChoices"]),
    },
    methods: {
        ...mapActions("usersAdmin", ["fetchUsers"]),
        ...mapMutations("usageLimits", ["incrementUsage"]),
        ...mapMutations("offPanel", ["closeOffPanel"]),
        onInvitationSent(userInvitation) {
            dispatchEvent(EVENTS.userInvited, userInvitation)
            this.fetchUsers()
            this.closeOffPanel("UserInvitationPanel")
        },
        onOpen() {
            this.userInvitation = _.clone(EMPTY_INVITATION_MODEL)
        },
    },
    i18n: {
        messages: {
            fr: {
                administrator: "Administrateur",
                administrator_description:
                    "Les administrateurs ont les mêmes permissions que les éditeurs et peuvent en outre configurer le desk (créer/modifier les canaux, tags, membres du desk, ..)",
                editor: "Editeur",
                editor_description:
                    "Les éditeurs peuvent voir et modifier tous les contenus du desk. Ils peuvent créer et modifier des projets.",
                emailAdress: "Adresse email",
                permissionMustBeSelected: "Choix d'une permission obligatoire",
                invitationError: "Erreur, invitation non envoyée",
                invitationHasBeenSent: "L'invitation a été envoyée",
                inviteNewUser: "Inviter une nouvel utilisateur",
                restricted_editor: "Editeur restreint",
                restricted_editor_description:
                    "Les éditeurs restreints peuvent uniquement voir et modifier les contenus au sein des projets et canaux dont ils sont responsables.",
                sendInvitation: "Envoyer l'invitation",
                teams: "Equipes",
                toWhichUserPermission: "Quelle permission affecter à cet utilisateur ?",
            },
            en: {
                administrator: "Administrator",
                administrator_description:
                    "Administrators have the same permissions as the editors and can also configure the desktop (create / edit channels, tags, desktop members, ...)",
                editor: "Editor",
                editor_description:
                    "Editors can view and edit all desktop content. They can create and modify projects.",
                emailAdress: "Email adress",
                permissionMustBeSelected: "You must select a permission",
                invitationError: "Error, invitation has not been sent",
                invitationHasBeenSent: "Invitation has been sent",
                inviteNewUser: "Invite new user",
                restricted_editor: "Restricted editor",
                restricted_editor_description:
                    "Restricted editors can only view and edit content within projects and channels for which they are responsible.",
                sendInvitation: "Send invitation",
                teams: "Teams",
                toWhichUserPermission: "Which permission do you want to assign this user?",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.UserInvitationPanel {
    background-color: $gray-lighter;
    border-radius: 0.3em;
    border: 1px solid #dce3e6;
    margin-bottom: 1rem;
}

.UserInvitationPanel__field__title {
    text-rendering: optimizeLegibility;
    font-weight: 400;
    line-height: 2em;
    font-size: 1em;
}

.UserInvitationPanel__field__radio {
    display: flex;
    margin: 1em 0;
}

.UserInvitationPanel__field__radio__input {
    align-self: flex-start;
    margin-top: 0.5em;
}

.UserInvitationPanel__field__radio__label {
    display: flex;
    flex-direction: column;
    margin-left: 0.5em;
}
</style>
