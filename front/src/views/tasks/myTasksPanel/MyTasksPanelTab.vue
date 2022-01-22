<template>
<div class="MyTasksPanelTab">
    <Loadarium name="fetchTasks">
        <div class="flex flex-col md:flex-row md:justify-start">
            <!-- Future tasks list -->
            <div class="w-full md:w-1/2 md:max-w-2xl md:mr-4 lg:mr-8">
                <h2 class="text-xl font-bold mb-4">
                    {{ $t("futureTasks") }}
                </h2>

                <template v-if="futureTasks.length">
                    <transition-group
                        enter-active-class="animated fadeInUp"
                        leave-active-class="animated fadeOutLeft"
                    >
                        <MyTasksPanelElement
                            v-for="task in futureTasks"
                            :key="task.id"
                            :listName="listName"
                            :task="task"
                        />
                    </transition-group>

                    <button
                        v-if="pagination && futureTasks.length"
                        class="button load-more w-full"
                        :disabled="pagination.next === null"
                        @click="loadMoreButton()"
                    >
                        <div v-if="pagination.next">
                            {{ $t("loadPage") }} {{ pagination.next }} / {{ pagination.num_pages }}
                        </div>
                        <div v-else>{{ $t("noMoreResults") }}</div>
                    </button>
                </template>

                <!-- No future tasks -->
                <div
                    v-else
                    class="text-lg text-gray-800 font-semibold leading-tight"
                >
                    {{ $t("noMoreTasks") }}
                    <div class="text-6xl">☕</div>
                </div>
            </div>

            <!-- Past tasks list -->
            <div class="w-full md:w-1/2 md:max-w-2xl">
                <h2 class="text-xl font-bold mb-4">
                    {{ $t("pastTasks") }}
                </h2>

                <template v-if="pastTasks.length">
                    <transition-group
                        enter-active-class="animated fadeInUp"
                        leave-active-class="animated fadeOutLeft"
                    >
                        <MyTasksPanelElement
                            v-for="task in pastTasks"
                            :key="task.id"
                            :listName="listName"
                            :task="task"
                        />
                    </transition-group>

                    <button
                        v-if="pagination && pastTasks.length"
                        class="button load-more w-full"
                        :disabled="pagination.next === null"
                        @click="loadMoreButton()"
                    >
                        <div v-if="pagination.next">
                            {{ $t("loadPage") }} {{ pagination.next }} / {{ pagination.num_pages }}
                        </div>
                        <div v-else>{{ $t("noMoreResults") }}</div>
                    </button>
                </template>

                <!-- No past tasks -->
                <div
                    v-else
                    class="text-lg text-gray-800 font-semibold leading-tight"
                >
                    {{ $t("noMoreTasks") }}
                    <div class="text-6xl">☕</div>
                </div>
            </div>
        </div>
    </Loadarium>
</div>
</template>

<script>
import moment from "moment"
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import PilotMixin from "@components/PilotMixin"

import MyTasksPanelElement from "./MyTasksPanelElement.vue"

export default {
    name: "MyTasksPanelTab",
    mixins: [PilotMixin],
    components: {
        MyTasksPanelElement,
    },
    props: {
        listName: String,
    },
    computed: {
        tasks() {
            return this.$store.state.tasks[this.listName].tasks
        },
        futureTasks() {
            let now = moment()
            return this.tasks.filter((t) => !t.deadline || moment(t.deadline) >= now)
        },
        pastTasks() {
            let now = moment()
            return this.tasks.filter((t) => moment(t.deadline) < now)
        },
        pagination() {
            return this.$store.state.tasks[this.listName].pagination
        },
    },
    methods: {
        ...mapActions("tasks", ["fetchTasks"]),
        loadMoreButton() {
            this.fetchTasks({
                listName: this.listName,
                append: true,
            })
        },
    },
    i18n: {
        messages: {
            fr: {
                futureTasks: "À venir",
                noTask: "Aucune task",
                noMoreTasks: "Aucune tâche en vue !",
                pastTasks: "Passées",
            },
            en: {
                futureTasks: "Forthcoming",
                noTask: "No task",
                noMoreTasks: "No task in sight !",
                pastTasks: "Past",
            },
        },
    },
}
</script>
