<template>
<div class="flex bg-white rounded p-4 border border-gray-200 mb-2">
    <div class="flex-grow">
        <div class="flex flex-col">
            <div
                v-if="userInvitation.email"
                class="UserInvitationElement__infos__email"
            >
                {{ userInvitation.email }}
            </div>
            <div
                v-if="permissionDisplay"
                class="UserInvitationElement__infos__detail"
            >
                {{ permissionDisplay }}
            </div>
            <div
                v-if="userInvitation.teams"
                class="UserInvitationElement__infos__detail"
            >
                <span v-for="team in userInvitation.teams">@{{ team.name }}</span>
            </div>
            <div class="UserInvitationElement__infos__detail">
                {{ $t("invitedAt") }} : {{ userInvitation.created_at | dateTimeFormat }}
            </div>
        </div>
    </div>

    <div
        v-if="currentRouteName === 'pending'"
        class="UserInvitationElement__actions"
    >
        <template v-if="deletionRequested">
            <SmartButtonSpinner
                class="button is-alert"
                :name="deleteUserInvitationName"
                :successText="$t('deleteInvitationSuccess')"
                @click="deleteUserInvitation(userInvitation)"
            >
                {{ $t("confirmDeletion") }}
            </SmartButtonSpinner>
            <a
                class="button is-white"
                @click="deletionRequested = false"
            >
                {{ $t("cancel") }}
            </a>
        </template>
        <template v-else-if="sendAgainRequested">
            <SmartButtonSpinner
                class="button is-blue"
                :name="sendAgainUserInvitationName"
                :successText="$t('sendAgainInvitationSuccess')"
                :timeout="4000"
                @click="sendAgainUserInvitation(userInvitation)"
                @reset="sendAgainRequested = false"
            >
                {{ $t("confirmSendAgain") }}
            </SmartButtonSpinner>
            <a
                class="button is-white"
                @click="sendAgainRequested = false"
            >
                {{ $t("cancel") }}
            </a>
        </template>
        <template v-else>
            <a
                class="button is-white"
                @click="sendAgainRequested = true"
            >
                {{ $t("sendAgain") }}
            </a>
            <a
                class="button"
                @click="deletionRequested = true"
            >
                {{ $t("delete") }}
            </a>
        </template>
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "UserInvitationElement",
    mixins: [PilotMixin],
    props: {
        userInvitation: Object,
    },
    data: () => ({
        deletionRequested: false,
        sendAgainRequested: false,
    }),
    computed: {
        ...mapGetters("usersAdmin", ["permissionsAvailable"]),
        deleteUserInvitationName() {
            return "deleteUserInvitation" + this.userInvitation.id
        },
        sendAgainUserInvitationName() {
            return "sendAgainUserInvitation" + this.userInvitation.id
        },
        permissionDisplay() {
            for (let perm of this.permissionsAvailable) {
                if (this.userInvitation.permission == perm.name) return perm.label
            }
        },
    },
    methods: {
        ...mapActions("usersAdmin", ["deleteUserInvitation", "sendAgainUserInvitation"]),
    },
    i18n: {
        messages: {
            fr: {
                confirmSendAgain: "Ok, renvoyer l'email",
                deleteInvitationSuccess: "Invitation supprimée",
                invitedAt: "Invitation envoyée",
                sendAgain: "Renvoyer l'email",
                sendAgainInvitationSuccess: "L'email a bien été renvoyé",
            },
            en: {
                confirmSendAgain: "Ok, send again",
                deleteInvitationSuccess: "Invitation deleted",
                invitedAt: "Invited",
                sendAgain: "Send the email again",
                sendAgainInvitationSuccess: "The email has been send correctly",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.UserInvitationElement {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: $gray-light 1px solid;
    border-radius: 5px;
    padding: 5px 10px;
    margin-bottom: 0.8em;
}

.UserInvitationElement__infos {
    display: flex;
    align-items: center;
    flex-flow: row wrap;
    justify-content: flex-start;
}
.UserInvitationElement__infos__email {
    font-weight: 600;
}
.UserInvitationElement__infos__detail {
    font-size: 0.9em;
    color: $gray;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

.UserInvitationElement__actions {
    display: flex;
    align-items: center;
    flex-flow: row wrap;
    justify-content: space-around;
    a:first-child {
        margin-right: 1.3em;
    }
    .button {
        margin: 0 0 0 1em;
    }
}

/* ==========================================================================
From 0 to 872
========================================================================== */

@media only screen and (max-width: 800px) {
    .UserInvitationElement {
        flex-direction: column;
        align-items: flex-start;
    }
}

@media only screen and (max-width: 500px) {
    .UserInvitationElement__actions {
        flex-direction: column;
        align-items: flex-start;

        .button {
            margin: 0.2rem 0;
        }
    }
}
</style>
