import _ from "lodash"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import { EVENTS, dispatchEvent } from "@js/events"
import VueI18n from "vue-i18n"

const PERMISSION_PILOT_ADMINS = "Administrators"
const PERMISSION_PILOT_EDITORS = "Editors"
const PERMISSION_RESTRICTED_EDITORS = "Restricted Editors"

let i18n = new VueI18n({
    locale: window.pilot.currentLocale,
    fallbackLocale: "fr",
    messages: {
        fr: {
            administrator: "Administrateur",
            editor: "Éditeur",
            restrictedEditor: "Éditeur restreint",
        },
        en: {
            administrator: "Administrator",
            editor: "Editor",
            restrictedEditor: "Restricted Editor",
        },
    },
})

export default {
    namespaced: true,
    state: () => ({
        // An array of the all the user currently in the <UserList> component
        userList: [],
        // The same users, but optionally filtered through Fuse
        filteredUsers: [],
        // The user on which we are selecting its teams with the <TeamPicker>
        userInTeamPick: {},
        // An array of all the teams in the <TeamList> component
        teams: [],
        // The users that we can quick add/remove to/from a team in the <TeamDetail> component
        quickUsers: [],
    }),
    mutations: {
        setUserList(state, userList) {
            state.userList = userList
        },
        setFilteredUsers(state, filteredUsers) {
            state.filteredUsers = filteredUsers
        },
        updateUser(state, user) {
            state.userList = state.userList.map((oldUser) =>
                oldUser.id == user.id ? user : oldUser,
            )
            if (state.userInTeamPick && state.userInTeamPick.id == user.id) {
                state.userInTeamPick = user
            }
        },
        prependToUserList(state, user) {
            state.userList.unshift(user)
        },
        removeUser(state, userId) {
            state.userList = state.userList.filter((user) => user.id != userId)
        },
        setUserInTeamPick(state, user) {
            state.userInTeamPick = user
        },
        setTeams(state, teams) {
            state.teams = teams
        },
        appendToTeams(state, team) {
            state.teams.push(team)
        },
        updateTeam(state, team) {
            state.teams = state.teams.map((oldTeam) => (oldTeam.id == team.id ? team : oldTeam))
        },
        removeTeam(state, team) {
            state.teams = state.teams.filter((t) => t.id != team.id)
        },
        setQuickUsers(state, quickUsers) {
            state.quickUsers = quickUsers
        },
        removeQuickUser(state, userId) {
            state.quickUsers = state.quickUsers.filter((user) => user.id != userId)
        },
        apendToQuickUser(state, user) {
            state.quickUsers.push(user)
        },
    },
    getters: {
        maxUsersReached(state, getters, rootState, rootGetters) {
            return rootGetters["usageLimits/usageLimitReached"]("users")
        },
        teamsChoices(state) {
            return state.teams.map((team) => ({ id: team.id, text: "@" + team.name }))
        },
        currentTeamDetail(state, getters, rootState, rootGetters) {
            if (rootGetters.currentRouteName != "teamDetail") {
                return null
            }
            return _.find(state.teams, (t) => t.id == rootState.route.params.id)
        },
        permissionsAvailable() {
            return [
                { name: PERMISSION_PILOT_ADMINS, label: i18n.t("administrator") },
                { name: PERMISSION_PILOT_EDITORS, label: i18n.t("editor") },
                { name: PERMISSION_RESTRICTED_EDITORS, label: i18n.t("restrictedEditor") },
            ]
        },
    },
    actions: {
        fetchUsers({ commit, getters, rootState, rootGetters }) {
            let url,
                params = {}
            if (rootGetters.currentRouteName == "actives") url = urls.users
            if (rootGetters.currentRouteName == "inactives") url = urls.usersInactives
            if (rootGetters.currentRouteName == "pending") url = urls.usersInvitation
            if (rootGetters.currentRouteName == "teamDetail") {
                url = urls.users
                params.teams = rootState.route.params.id
            }

            $httpX({
                name: "fetchUsers",
                method: "GET",
                commit,
                params,
                url,
            }).then((response) => {
                commit("setFilteredUsers", [])
                let userList = response.data
                // Sort user invitations by creation date
                if (rootGetters.currentRouteName == "pending") {
                    userList = _.sortBy(userList, (userInvitation) => userInvitation.created_at)
                }
                commit("setUserList", userList)
            })
        },

        deactivateUser({ commit, dispatch, rootState }, user) {
            let loadingName = "changeActiveStatus" + user.id
            return $httpX({
                name: loadingName,
                commit,
                method: "PUT",
                url: urls.usersDeactivate.format({ id: user.id }),
            }).then((response) => {
                dispatchEvent(EVENTS.userDeactivated, user)
                setTimeout(() => {
                    commit("loading/resetLoading", loadingName, { root: true })
                    commit("removeUser", user.id)
                }, 4000)
            })
        },

        reactivateUser({ commit, dispatch, rootState }, user) {
            let loadingName = "changeActiveStatus" + user.id
            return $httpX({
                name: loadingName,
                commit,
                method: "PUT",
                url: urls.usersReactivate.format({ id: user.id }),
            }).then((response) => {
                dispatchEvent(EVENTS.userReactivated, user)
                setTimeout(() => {
                    commit("loading/resetLoading", loadingName, { root: true })
                    commit("removeUser", user.id)
                }, 4000)
            })
        },

        updateUserPermission({ commit }, { user, permission }) {
            return $httpX({
                name: "updateUserPermission" + user.id,
                commit,
                method: "PUT",
                url: urls.usersUpdatePermission.format({ id: user.id }),
                data: { permission },
            }).then((response) => {
                commit("updateUser", response.data)
            })
        },

        wipeoutUser({ commit }, user) {
            return $httpX({
                name: "wipeoutUser" + user.id,
                commit,
                method: "POST",
                url: urls.usersWipeout.format({ id: user.id }),
            }).then((response) => {
                setTimeout(() => {
                    commit("removeUser", user.id)
                }, 4000)
            })
        },

        deleteUserInvitation({ commit, rootState }, userInvitation) {
            let loadingName = "deleteUserInvitation" + userInvitation.id
            return $httpX({
                name: loadingName,
                commit,
                method: "DELETE",
                url: urls.usersInvitation.format({ id: userInvitation.id }),
            }).then((response) => {
                dispatchEvent(EVENTS.userDeinvited, userInvitation)
                setTimeout(() => {
                    commit("loading/resetLoading", loadingName, { root: true })
                    commit("removeUser", userInvitation.id)
                }, 4000)
            })
        },

        sendAgainUserInvitation({ commit }, userInvitation) {
            return $httpX({
                name: "sendAgainUserInvitation" + userInvitation.id,
                commit,
                method: "POST",
                url: urls.usersInvitationSendAgain.format({ id: userInvitation.id }),
            })
        },

        updateUserTeams({ commit }, { user, teams_id }) {
            let loadingName = "updateUserTeams" + user.id
            return $httpX({
                name: loadingName,
                commit,
                method: "PUT",
                url: urls.usersUpdateTeams.format({ id: user.id }),
                data: { teams_id },
            }).then((response) => {
                commit("updateUser", response.data)
                return response
            })
        },

        fetchTeams({ commit }) {
            $httpX({
                name: "fetchTeams",
                method: "GET",
                commit,
                url: urls.teams,
            }).then((response) => {
                commit("setTeams", response.data)
            })
        },

        deleteTeam({ commit }, team) {
            return $httpX({
                name: "deleteTeam" + team.id,
                commit,
                method: "DELETE",
                url: urls.teams.format({ id: team.id }),
            }).then((response) => {
                // Remove the team from the list
                commit("removeTeam", team)
                dispatchEvent(EVENTS.teamDeleted, team)
            })
        },

        fetchQuickUsers({ commit, rootState }) {
            $httpX({
                name: "fetchQuickUsers",
                method: "GET",
                commit,
                params: {
                    // Exclude the user which are already in the current team
                    Xteams: rootState.route.params.id,
                },
                url: urls.users,
            }).then((response) => {
                commit("setQuickUsers", response.data)
            })
        },

        // Quick add a user to the currentTeamDetail
        quickAddToTeam({ commit, getters, dispatch }, user) {
            dispatch("updateUserTeams", {
                user,
                teams_id: _.concat(user.teams_id, getters.currentTeamDetail.id),
            }).then((response) => {
                commit("prependToUserList", response.data)
                commit("removeQuickUser", response.data.id)
            })
        },

        // Quick remove a user from the currentTeamDetail
        quickRemoveFromTeam({ commit, getters, dispatch }, user) {
            dispatch("updateUserTeams", {
                user,
                teams_id: _.without(user.teams_id, getters.currentTeamDetail.id),
            }).then((response) => {
                setTimeout(() => {
                    commit("removeUser", user.id)
                }, 2000)
                commit("apendToQuickUser", response.data)
            })
        },
    },
}
