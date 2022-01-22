<template>
<div class="bg-white rounded border border-gray-200 p-4 flex flex-grow mb-2">
    <div class="UserListElement__infos flex items-center flex-grow">
        <UserAvatar
            size="45px"
            :user="user"
        />
        <div class="ml-4">
            <div
                v-if="user.username"
                class="font-semibold"
            >
                {{ user.first_name }} {{ user.last_name }} (
                <UserDisplay :user="user" />
                )
            </div>
            <div
                v-if="user.email"
                class="text-sm text-gray-700"
            >
                {{ user.email }}
            </div>
            <div
                v-if="user.job"
                class="text-sm text-gray-700"
            >
                {{ user.job }}
            </div>
            <div
                v-if="user.teams"
                class="text-sm text-gray-700"
            >
                <span v-for="team in user.teams">@{{ team.name }}</span>
            </div>
        </div>
    </div>

    <div
        v-if="currentRouteName === 'actives'"
        class="flex flex-shrink-0 items-center"
    >
        <div class="mr-2">
            <Loading :name="updateUserPermissionName" />
            <div
                v-if="loadingStatus[updateUserPermissionName] === 'success'"
                class="text-green-600"
            >
                {{ updateUserPermissionResponse }}
            </div>
            <div
                v-if="loadingStatus[updateUserPermissionName] === 'error'"
                class="UserListElement__selectgroup text-red-600"
            >
                {{ updateUserPermissionResponse }}
            </div>
            <select
                v-if="!loadingStatus[updateUserPermissionName]"
                class="border border-gray-300 h-8 bg-white"
                :value="user.permission"
                @change="onPermissionChanged"
            >
                <option
                    v-for="permission in permissionsAvailable"
                    :value="permission.name"
                >
                    {{ permission.label }}
                </option>
            </select>
        </div>

        <button
            class="button mr-2"
            @click="startTeamPick"
        >
            {{ $t("selectTeams") }}
        </button>

        <SmartButtonSpinner
            :class="activeStatusButtonsState"
            :name="changeActiveStatusName"
            :successText="$t('deactivateSuccessText')"
            @click="deactivateUser(user)"
        >
            {{ $t("deactivate") }}
        </SmartButtonSpinner>
    </div>
    <div
        v-if="currentRouteName === 'inactives'"
        class="UserListElement__actions"
    >
        <button
            v-if="maxUsersReached"
            class="button hollow"
            disabled
        >
            {{ $t("maxUsersReached") }}
        </button>

        <template v-else-if="wipeoutRequested">
            <span
                v-html="$t('deletionWarningMessage')"
                class="UserListElement__deletionWarningMessage"
            />

            <SmartButtonSpinner
                class="button is-alert"
                :name="wipeoutUserName"
                @click="wipeoutUser(user)"
            >
                {{ $t("confirmDeletion") }}
            </SmartButtonSpinner>
            <a
                class="button hollow secondary"
                @click="wipeoutRequested = false"
            >
                {{ $t("cancel") }}
            </a>
        </template>
        <template v-else>
            <SmartButtonSpinner
                :class="activeStatusButtonsState"
                :name="changeActiveStatusName"
                :successText="$t('activationSuccessText')"
                @click="reactivateUser(user)"
            >
                {{ $t("activate") }}
            </SmartButtonSpinner>

            <button
                class="button hollow alert"
                @click="wipeoutRequested = true"
            >
                {{ $t("delete") }}
            </button>
        </template>
    </div>
    <div
        v-if="currentRouteName === 'teamDetail'"
        class="UserListElement__actions"
    >
        <SmartButtonSpinner
            class="hollow"
            :name="updateUserTeamName"
            @click="quickRemoveFromTeam(user)"
        >
            {{ $t("removeFromTeam") }}
        </SmartButtonSpinner>
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "UserListElement",
    mixins: [PilotMixin],
    props: {
        user: Object,
    },
    data: () => ({
        updateUserPermissionResponse: "",
        wipeoutRequested: false,
    }),
    computed: {
        ...mapState("loading", ["loadingStatus"]),
        ...mapGetters("usersAdmin", ["maxUsersReached", "permissionsAvailable"]),
        ...mapGetters("loading", ["getErrorMessage"]),
        changeActiveStatusName() {
            return "changeActiveStatus" + this.user.id
        },
        updateUserPermissionName() {
            return "updateUserPermission" + this.user.id
        },
        updateUserTeamName() {
            return "updateUserTeams" + this.user.id
        },
        wipeoutUserName() {
            return "wipeoutUser" + this.user.id
        },
        activeStatusButtonsState() {
            return {
                primary: !this.loadingStatus[this.changeActiveStatusName],
                hollow: !this.loadingStatus[this.changeActiveStatusName],
            }
        },
    },
    methods: {
        ...mapMutations("usersAdmin", ["setUserInTeamPick"]),
        ...mapActions("usersAdmin", [
            "reactivateUser",
            "deactivateUser",
            "updateUserPermission",
            "quickRemoveFromTeam",
            "wipeoutUser",
        ]),
        ...mapMutations("loading", ["resetLoading"]),
        startTeamPick() {
            this.setUserInTeamPick(this.user)
            this.openOffPanel("teamPicker")
        },
        onPermissionChanged(event) {
            this.updateUserPermission({
                user: this.user,
                permission: event.target.value,
            })
                .then((response) => {
                    this.updateUserPermissionResponse = this.$t("updateOK")
                    setTimeout(() => {
                        this.resetLoading(this.updateUserPermissionName)
                        this.updateUserPermissionResponse = ""
                    }, 5000)
                })
                .catch((error) => {
                    this.updateUserPermissionResponse = this.getErrorMessage(
                        this.updateUserPermissionName,
                    )
                    setTimeout(() => {
                        this.resetLoading(this.updateUserPermissionName)
                        this.updateUserPermissionResponse = ""
                    }, 5000)
                })
        },
    },
    i18n: {
        messages: {
            fr: {
                activate: "Activer",
                activationSuccessText: "Utilisateur activé ",
                deactivate: "Désactiver",
                deactivateSuccessText: "Utilisateur désactivé",
                deletionWarningMessage:
                    "Attention, l'utilisateur ne sera pas récupérable.<br />Les données produites par cet utilisateur resteront disponibles.",
                error: "Une erreur s'est produite",
                selectTeams: "Choisir équipes",
                removeFromTeam: "Retirer de l'équipe",
                updateOK: "Modification enregistrée",
                maxUsersReached: "Activation impossible, maximum atteint",
            },
            en: {
                activate: "Activate",
                activationSuccessText: "User activated",
                deactivate: "Deactivate",
                deactivateSuccessText: "User disabled",
                deletionWarningMessage:
                    "Warning : the user won't be recoverable.<br />The data produced by this user will stay available.",
                error: "An error has occurred",
                selectTeams: "Select teams",
                removeFromTeam: "Remove from team",
                updateOK: "Update saved!",
                maxUsersReached: "Activation impossible, maximum reached",
            },
        },
    },
}
</script>
