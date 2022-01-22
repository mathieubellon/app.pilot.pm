<template>
<MainLayout>
    <template #title>
        {{ $t("users") }}
    </template>

    <template #actions>
        <UseraAdminTopBarActions />
    </template>

    <template #middlebar>
        <UserTabs />
    </template>

    <template #content>
        <div class="container mx-auto p-5">
            <router-view :key="currentRouteName" />
        </div>
    </template>
</MainLayout>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import MainLayout from "@components/layout/MainLayout"
import UserTabs from "./UserTabs"
import UseraAdminTopBarActions from "./UseraAdminTopBarActions"

export default {
    name: "UserAdminApp",
    mixins: [PilotMixin],
    components: {
        MainLayout,
        UserTabs,
        UseraAdminTopBarActions,
    },
    methods: {
        ...mapActions("usersAdmin", ["fetchTeams"]),
    },
    created() {
        this.fetchTeams()
    },
}
</script>
