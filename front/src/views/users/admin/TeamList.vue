<template>
<div>
    <Loadarium name="fetchTeams">
        <AdminList
            :instancesList="sortedTeams"
            :sortable="false"
            @delete="deleteTeam"
            @edit="$refs.form.openFormPanel($event)"
        >
            <div
                class="flex justify-between items-center w-full"
                slot-scope="{ instance }"
            >
                <div class="flex flex-col">
                    <span class="font-bold">
                        {{ instance.name }}
                    </span>

                    <span class="text-gray-600">
                        {{ instance.description }}
                    </span>
                </div>
                <AdminButton
                    aClass="button text-blue-600 -mr-5 sm:ml-4"
                    @click="$router.push({ name: 'teamDetail', params: { id: instance.id } })"
                >
                    {{ $t("selectUsers") }}
                </AdminButton>
            </div>
        </AdminList>

        <div
            v-if="teams.length === 0"
            class="help-text"
        >
            <div class="help-text-title">
                <Icon
                    class="help-text-icon"
                    name="Users"
                />
                <span>{{ $t("teamListEmpty") }}</span>
            </div>
            <div class="help-text-content">
                {{ $t("explainTeams") }}
            </div>
            <button
                class="button is-blue"
                @click="$refs.form.openFormPanel()"
            >
                {{ $t("createTeam") }}
            </button>
        </div>
    </Loadarium>

    <AutoFormInPanel
        name="teamForm"
        ref="form"
        :saveUrl="urls.teams"
        :schema="teamFormSchema"
        :title="$t('createTeam')"
        @created="onTeamCreated"
        @updated="onTeamUpdated"
    />
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { EVENTS, dispatchEvent } from "@js/events"
import { sortByAlphaString } from "@js/utils.js"
import PilotMixin from "@components/PilotMixin"

import AdminList from "@components/admin/AdminList.vue"
import AdminButton from "@components/admin/AdminButton"

export default {
    name: "TeamList",
    mixins: [PilotMixin],
    components: {
        AdminList,
        AdminButton,
    },
    computed: {
        ...mapState("usersAdmin", ["teams"]),
        sortedTeams() {
            return sortByAlphaString(this.teams, (team) => team.name)
        },
        teamFormSchema() {
            return [
                {
                    name: "name",
                    type: "char",
                    label: this.$t("name"),
                    placeholder: this.$t("name"),
                    required: true,
                },
                {
                    name: "description",
                    type: "text",
                    label: this.$t("description"),
                    placeholder: this.$t("description"),
                },
            ]
        },
    },
    methods: {
        ...mapMutations("usersAdmin", ["appendToTeams", "updateTeam"]),
        ...mapActions("usersAdmin", ["deleteTeam"]),
        onTeamCreated(team) {
            this.appendToTeams(team)
            dispatchEvent(EVENTS.teamCreated, team)
        },
        onTeamUpdated(team) {
            this.updateTeam(team)
            dispatchEvent(EVENTS.teamUpdated, team)
        },
    },
    i18n: {
        messages: {
            fr: {
                createTeam: "Créer une équipe",
                explainTeams:
                    "Les équipes regroupent plusieurs utilisateurs pour pouvoir les @mentionner rapidement",
                selectUsers: "Gérer les utilisateurs",
                teamListEmpty: "Vous n'avez pas encore créé d'équipe",
            },
            en: {
                createTeam: "Create a team",
                explainTeams: "Teams groups multiple users to @mention them quickly",
                selectUsers: "Manage users",
                teamListEmpty: "You haven't created any team yet",
            },
        },
    },
}
</script>
