<template>
<div class="flex flex-grow tabs">
    <router-link
        class="tab"
        active-class="is-active"
        :to="{ name: 'actives' }"
    >
        {{ $t("activesUsers") }}
    </router-link>

    <router-link
        class="tab"
        active-class="is-active"
        :to="{ name: 'pending' }"
    >
        {{ $t("pendingInvitations") }}
    </router-link>

    <router-link
        class="tab"
        active-class="is-active"
        :to="{ name: 'inactives' }"
    >
        {{ $t("inactivesUsers") }}
    </router-link>

    <router-link
        class="tab"
        active-class="is-active"
        :to="{ name: 'teams' }"
    >
        {{ $t("teams") }}
    </router-link>

    <router-link
        v-if="currentTeamDetail"
        class="tab"
        active-class="is-active"
        :to="{ name: 'teamDetail', params: { id: currentTeamDetail.id } }"
    >
        {{ $t("team") }} : {{ currentTeamDetail.name }}
    </router-link>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "UserTabs",
    mixins: [PilotMixin],
    computed: {
        ...mapGetters("usersAdmin", ["currentTeamDetail"]),
    },
    i18n: {
        messages: {
            fr: {
                activesUsers: "Utilisateurs actifs",
                inactivesUsers: "Utilisateurs inactifs",
                pendingInvitations: "Invitations en attente",
                teams: "Equipes",
                team: "Equipe",
            },
            en: {
                activesUsers: "Actives users",
                inactivesUsers: "Inactives users",
                pendingInvitations: "Pending invitations",
                teams: "Teams",
                team: "Team",
            },
        },
    },
}
</script>
