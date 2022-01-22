<template>
<MainLayout>
    <template #title>
        <span v-if="currentTaskGroup">{{ currentTaskGroup.name }}</span>
        <span v-else>{{ $t("taskGroup") }}</span>
    </template>

    <template #actions>
        <AdminButton
            v-show="currentRouteName == 'taskGroupList'"
            @click="openOffPanel('taskGroupForm')"
        >
            {{ $t("createTaskGroup") }}
        </AdminButton>
    </template>

    <template #content>
        <div class="container mx-auto p-5">
            <transition
                slot="main"
                enter-active-class="animated animated-150 fadeIn"
                leave-active-class="animated animated-150 fadeOut"
                mode="out-in"
            >
                <router-view />
            </transition>
        </div>
    </template>
</MainLayout>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import MainLayout from "@components/layout/MainLayout"
import AdminButton from "@components/admin/AdminButton"

export default {
    name: "TaskGroupAdminApp",
    mixins: [PilotMixin],
    components: {
        MainLayout,
        AdminButton,
    },
    computed: {
        ...mapState("taskGroup", ["taskGroups", "currentTaskGroup"]),
    },
    methods: {
        ...mapMutations("taskGroup", ["setCurrentTaskGroup"]),
        ...mapActions("taskGroup", ["fetchTaskGroups"]),
        updateCurrentTaskGroup() {
            this.setCurrentTaskGroup(
                _.find(this.taskGroups, { id: _.toInteger(this.$route.params.id) }),
            )
        },
    },
    watch: {
        "$route.params.id"() {
            this.updateCurrentTaskGroup()
        },
        taskGroups() {
            this.updateCurrentTaskGroup()
        },
    },
    created() {
        this.fetchTaskGroups()
    },
    i18n: {
        messages: {
            fr: {
                createTaskGroup: "Créer un groupe de tâches",
            },
            en: {
                createTaskGroup: "Create a task group",
            },
        },
    },
}
</script>
