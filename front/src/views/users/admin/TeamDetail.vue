-
<template>
<div class="TeamDetail">
    <div class="flex flex-row justify-between w-full mb-4">
        <router-link :to="{ name: 'teams' }">< {{ $t("back") }}</router-link>

        <span>
            {{ currentTeamDetail && currentTeamDetail.name }}
        </span>

        <!-- This is a spacer to center the team name -->
        <span />
    </div>

    <Loadarium name="fetchQuickUsers">
        <div class="TeamDetail__QuickAddUser">
            <SelectInput
                class="is-white"
                :choices="quickUsersChoices"
                :placeholder="$t('addUserToTeam')"
                :reduce="(user) => user"
                :resetOnOptionsChange="true"
                @input="onUserAdded"
            />
        </div>
    </Loadarium>

    <Loadarium name="fetchUsers">
        <transition-group
            enter-active-class="animated fadeInRight"
            leave-active-class="animated fadeOutRight"
        >
            <UserListElement
                v-for="user in userList"
                :key="user.id"
                :user="user"
            />
        </transition-group>
    </Loadarium>

    <div
        v-if="userList.length == 0"
        class="help-text"
    >
        <div class="help-text-title">
            <Icon
                class="help-text-icon"
                name="Users"
            />
            <span>{{ $t("noUserInTeam") }}</span>
        </div>
        <div class="help-text-content">
            {{ $t("explainTeams") }}
        </div>
    </div>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import UserListElement from "./UserListElement.vue"

export default {
    name: "TeamDetail",
    mixins: [PilotMixin],
    components: {
        UserListElement,
    },
    computed: {
        ...mapState("usersAdmin", ["userList", "quickUsers"]),
        ...mapGetters("usersAdmin", ["currentTeamDetail"]),
        quickUsersChoices() {
            return this.quickUsers.map((user) => ({
                value: user.id,
                label: "@" + user.username,
                user,
            }))
        },
    },
    methods: {
        ...mapActions("usersAdmin", ["fetchUsers", "fetchQuickUsers", "quickAddToTeam"]),
        onUserAdded(choice) {
            if (choice) {
                this.quickAddToTeam(choice.user)
            }
        },
    },
    mounted() {
        this.fetchUsers()
        this.fetchQuickUsers()
    },
    i18n: {
        messages: {
            fr: {
                addUserToTeam: "Ajouter un utilisateur à l'équipe...",
                back: "Retour",
                explainTeams:
                    "Les équipes regroupent plusieurs utilisateurs pour pouvoir les @mentionner rapidement",
                noUserInTeam: "Aucun utilisateur dans l'équipe",
            },
            en: {
                addUserToTeam: "Add a user to this team...",
                back: "Back",
                explainTeams: "Teams groups multiple users to @mention them quickly",
                noUserInTeam: "No user in this team",
            },
        },
    },
}
</script>

<style lang="scss">
.TeamDetail__QuickAddUser {
    margin-bottom: 1em;
}
</style>
