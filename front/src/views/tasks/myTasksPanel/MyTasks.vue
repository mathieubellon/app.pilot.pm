<template>
<MainLayout>
    <template #title>
        {{ $t("myTasks") }}
    </template>

    <template #middlebar>
        <div class="tabs">
            <a
                :class="['tab', { 'is-active': currentTab == 'undone' }]"
                @click.prevent="currentTab = 'undone'"
            >
                <span>{{ $t("undone") }}</span>
                ( {{ undoneCount }} )
            </a>

            <a
                :class="['tab', { 'is-active': currentTab == 'done' }]"
                @click.prevent="currentTab = 'done'"
            >
                <span>{{ $t("done") }}</span>
                ( {{ doneCount }} )
            </a>
        </div>
    </template>

    <template #content>
        <div class="p-2 md:p-8">
            <!-- Undone tasks -->
            <div
                v-if="currentTab == 'undone'"
                class="undoneTab"
                key="undoneTab"
            >
                <MyTasksPanelTab listName="undone" />
            </div>

            <!-- Done tasks -->
            <div
                v-if="currentTab == 'done'"
                key="doneTab"
            >
                <MyTasksPanelTab listName="done" />
            </div>
        </div>
    </template>
</MainLayout>
</template>

<script>
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import PilotMixin from "@components/PilotMixin"

import MyTasksPanelTab from "./MyTasksPanelTab.vue"

import MainLayout from "@components/layout/MainLayout"

export default {
    name: "MyTasks",
    mixins: [PilotMixin],
    components: {
        MyTasksPanelTab,
        MainLayout,
    },
    data: () => ({
        currentTab: "undone",
    }),
    computed: {
        ...mapGetters("tasks", ["undoneCount", "doneCount"]),
    },
    methods: {
        ...mapMutations("users", ["setUnreadNotificationCount"]),
        ...mapActions("tasks", ["fetchTasks"]),
        fetchAllTabs() {
            this.fetchTasks({ listName: "undone" })
            this.fetchTasks({ listName: "done" })
        },
    },
    created() {
        this.fetchAllTabs()
    },
    i18n: {
        messages: {
            fr: {
                undone: "à faire",
                done: "faites",
                myTasks: "Mes tâches",
            },
            en: {
                undone: "Undone",
                done: "Done",
                myTasks: "My Tasks",
            },
        },
    },
}
</script>
