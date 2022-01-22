<template>
<div>
    <UserInvitationPanel />
    <div class="p-5 mb-4 bg-gray-50 border-l-2 border-blue-500 text-gray-700">
        <span v-if="usageLimits.users.max_usage != -1">
            {{
                $t("usersUsage", {
                    usage: usageLimits.users.current_usage,
                    maxUsers: usageLimits.users.max_usage,
                    users: usageLimits.users.extra.users,
                    invitations: usageLimits.users.extra.invitations,
                })
            }}
        </span>
        <span v-else>
            {{ $t("usersUnlimited") }}
        </span>
    </div>
    <div
        v-if="userList.length > 0"
        class="flex justify-between mb-4"
    >
        <VueFuse
            ref="fuseInput"
            :defaultAll="true"
            :keys="['first_name', 'last_name', 'email']"
            :list="userList"
            :placeholder="$t('search')"
            :shouldSort="currentRouteName != 'pending'"
            :threshold="0.1"
            @result="setFilteredUsers"
        />
    </div>

    <Loadarium name="fetchUsers">
        <template v-if="currentRouteName == 'pending'">
            <UserInvitationElement
                v-for="userInvitation in filteredUsers"
                :key="userInvitation.id"
                :userInvitation="userInvitation"
            />
        </template>
        <template v-else>
            <UserListElement
                v-for="user in filteredUsers"
                :key="user.id"
                :user="user"
            />
        </template>

        <div v-if="filteredUsers.length === 0">
            <div
                v-if="hasSearchValue()"
                class="UserList__searchResults"
                key="filteredUserList"
            >
                {{ $t("noResults") }}
            </div>
            <div
                v-else
                class="UserList__emptyState"
            >
                <div
                    v-if="currentRouteName === 'pending'"
                    class="UserList__emptyState__element"
                >
                    <h3>{{ $t("noInvitation") }}</h3>
                    <h4>{{ $t("invitationListEmpty") }}</h4>
                    <button
                        class="button is-blue"
                        @click="openOffPanel('UserInvitationPanel')"
                    >
                        {{ $t("sendInvitation") }}
                    </button>
                </div>
                <div
                    v-if="currentRouteName === 'inactives'"
                    class="UserList__emptyState__element"
                >
                    <h3>{{ $t("noAccountDeactivated") }}</h3>
                    <h4>{{ $t("deactivationHelpText") }}</h4>
                </div>
            </div>
        </div>
    </Loadarium>

    <OffPanel name="teamPicker">
        <div slot="offPanelTitle">{{ $t("selectTeams") }}</div>
        <TeamPicker
            slot="offPanelBody"
            :loading="loadingInProgress['updateUserTeams' + userInTeamPick.id]"
            :multiple="true"
            :pickedTeamsId="userInTeamPick.teams_id"
            :teams="teams"
            @pick="onTeamPicked"
        />
    </OffPanel>
</div>
</template>

<script>
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"
import PilotMixin from "@components/PilotMixin"

import TeamPicker from "@components/picker/TeamPicker.vue"
import UserListElement from "./UserListElement.vue"
import UserInvitationElement from "./UserInvitationElement.vue"
import UserInvitationPanel from "./UserInvitationPanel.vue"

export default {
    name: "UserList",
    mixins: [PilotMixin],
    components: {
        TeamPicker,
        UserListElement,
        UserInvitationElement,
        UserInvitationPanel,
    },
    computed: {
        ...mapState("usersAdmin", ["userList", "filteredUsers", "userInTeamPick", "teams"]),
        ...mapState("usageLimits", ["usageLimits"]),
        ...mapState("loading", ["loadingInProgress"]),
    },
    watch: {
        currentRouteName() {
            this.fetchUsers()
        },
    },
    methods: {
        ...mapMutations("usersAdmin", ["setFilteredUsers"]),
        ...mapActions("usersAdmin", ["fetchUsers", "updateUserTeams"]),
        hasSearchValue() {
            return this.$refs.fuseInput && this.$refs.fuseInput.search != ""
        },
        onTeamPicked(teams_id) {
            this.updateUserTeams({
                user: this.userInTeamPick,
                teams_id: teams_id,
            })
        },
    },
    mounted() {
        this.fetchUsers()
    },
    i18n: {
        messages: {
            fr: {
                activate: "Activer",
                closeForm: "Fermer le formulaire d'invitation",
                deactivate: "Désactiver",
                deactivationHelpText:
                    "Lorsque vous désactivez un compte il sera conservé ici pour archive. Vous pourrez l'activer à nouveau depuis cette liste",
                usersUsage:
                    "Vous utilisez {usage} des {maxUsers} places comprises dans votre licence ({users} utilisateurs actifs et {invitations} invitations en attente)",
                usersUnlimited: "Votre compte vous autorise un nombre illimité de places",
                emptyUserList:
                    "Votre liste d'utilisateurs est vide, invitez d'autres personnes à vous rejoindre",
                invitationListEmpty:
                    "Votre liste d'invitation est vide, invitez d'autres personnes à vous rejoindre",
                noAccountDeactivated: "Aucun compte désactivé pour le moment !",
                noInvitation: "Aucune invitation !",
                noUser: "Aucun utilisateur !",
                selectTeams: "Choisir équipes",
                sendInvitation: "Envoyer une invitation",
            },
            en: {
                activate: "Activate",
                closeForm: "Close invitation form",
                deactivate: "Désactiver",
                deactivationHelpText:
                    "When you disable an account it will be kept here for archive. You can activate it again from this list",
                usersUsage:
                    "You use {usage} of the {maxUsers} places included in your license ({users} active users and {invitations} pending invitations)",
                usersUnlimited: "Unlimited seats licence",
                emptyUserList: "Your list of users is empty, invite others to join you",
                invitationListEmpty: "Your invitation list is empty, invite others to join you",
                noAccountDeactivated: "No account disabled yet!",
                noInvitation: "No invitation !",
                noUser: "No user!",
                selectTeams: "Select teams",
                sendInvitation: "Send an invitation",
            },
        },
    },
}
</script>

<style lang="scss">
.UserList__emptyState {
    display: flex;
    justify-content: center;
}
.UserList__emptyState__element {
    display: flex;
    justify-content: center;
    flex-direction: column;
    align-items: center;
    text-align: center;
    max-width: 600px;

    h4 {
        color: #939393;
        margin-bottom: 2em;
        line-height: 1.5em;
    }
}
.UserList__searchResults {
    background-color: aliceblue;
}
</style>
