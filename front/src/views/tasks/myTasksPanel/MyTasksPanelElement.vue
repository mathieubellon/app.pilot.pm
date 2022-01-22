<template>
<div class="MyTasksPanelElement">
    <div class="flex items-center justify-between text-sm">
        <div
            v-if="task.deadline"
            class="Task__deadline"
            :class="{ late: !task.done && isLate }"
        >
            <Icon
                class="w-4 mr-2"
                name="Calendar"
            />
            {{ task.deadline | dateFormat }} ({{ endOfDayDeadline | timeAgo }})
        </div>

        <div
            v-if="!task.deadline"
            class="Task__deadline"
        >
            <Icon
                class="w-4 mr-2"
                name="Calendar"
            />
            {{ $t("noDeadline") }}
        </div>
        <SmartLink
            class="Task__content"
            :class="{ isDone: task.done }"
            :to="task.url"
        >
            {{ $t("goto") }}
            <Icon
                class="text-gray-600 w-4"
                name="ChevronRight"
            />
        </SmartLink>
    </div>

    <div
        class="Task__info"
        :class="{ 'bg-gray-200': task.done }"
    >
        <div
            class="Task__name flex items-center"
            :class="{ 'line-through text-gray-400': task.done }"
        >
            {{ task.name }}
        </div>
        <div
            v-if="task.project"
            class="Task__linkedItem"
        >
            {{ $t("inProject") }}
            <SmartLink
                class="underline"
                :to="task.url"
            >
                {{ task.project.name }} #{{ task.project.id }}
            </SmartLink>
        </div>
        <div
            v-if="task.item"
            class="Task__linkedItem"
        >
            {{ $t("inItem") }}
            <SmartLink
                class="underline"
                :to="task.url"
            >
                {{ task.item.title }} #{{ task.item.id }}
            </SmartLink>
        </div>
        <div
            v-if="task.channel"
            class="Task__linkedItem"
        >
            {{ $t("inChannel") }}
            <SmartLink
                class="underline"
                :to="task.url"
            >
                {{ task.channel.name }}
            </SmartLink>
        </div>
    </div>

    <div v-if="toggleTaskDoneRequested">
        <SmartButtonSpinner
            class="button is-blue is-small my-2"
            :name="'toggleTaskDone' + task.id"
            @click="confirmToggleTaskDone()"
        >
            {{ $t("confirm") }}
        </SmartButtonSpinner>

        <button
            class="button is-small my-2 text-gray-600"
            @click.prevent="cancelToggleTaskDone()"
        >
            {{ $t("cancel") }}
        </button>
    </div>
    <div
        v-else
        class="Task__toggleTaskDone"
        @click="requestToggleTaskDone()"
    >
        <a
            v-if="task.done"
            class="button is-small my-2 text-gray-600"
        >
            {{ $t("markTaskAsUndone") }}
        </a>
        <a
            v-else
            class="button is-small my-2 text-gray-600"
        >
            {{ $t("markTaskAsDone") }}
        </a>
    </div>
</div>
</template>

<script>
import moment from "moment"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "MyTasksPanelElement",
    mixins: [PilotMixin],
    props: ["task"],
    data: () => ({
        toggleTaskDoneRequested: false,
    }),
    computed: {
        endOfDayDeadline() {
            return moment(this.task.deadline).add(1, "days")
        },
        isLate() {
            return moment(this.endOfDayDeadline) < moment()
        },
    },
    methods: {
        ...mapActions("tasks", ["toggleTaskDone"]),
        requestToggleTaskDone() {
            this.toggleTaskDoneRequested = true
        },
        confirmToggleTaskDone() {
            this.toggleTaskDoneRequested = false
            this.toggleTaskDone(this.task)
        },
        cancelToggleTaskDone() {
            this.toggleTaskDoneRequested = false
        },
    },
    i18n: {
        messages: {
            fr: {
                doItFor: "Date limite : ",
                markTaskAsDone: "Marquer comme réalisée",
                markTaskAsUndone: "Annuler : Marquer comme non réalisée",
                noDeadline: "Cette tâche n'a pas de date de rendu",
                goto: "Ouvrir",
                inChannel: "Dans le canal",
                inProject: "Dans le projet",
                inItem: "Dans le contenu",
            },
            en: {
                doItFor: "Deadline",
                markTaskAsDone: "Mark task as done",
                markTaskAsUndone: "Mark as undone",
                noDeadline: "No deadline",
                inChannel: "In the channel",
                inProject: "In the project",
                inItem: "In the content",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/include_media.scss";
.MyTasksPanelElement {
    @apply flex flex-col border border-gray-200 rounded bg-white my-2 p-3 w-full;
}
.Task__info {
    @apply flex flex-col text-blue-900 my-2 rounded p-2 break-words;
    background-color: #f4f5f7;
}
.Task__name {
    font-size: 20px;
    line-height: 24px;
    color: #172b4d;
}
.Task__linkedItem,
.Task__linkedItem a {
    font-size: 14px;
    line-height: 20px;
    color: #5e6c84;
}
.Task__deadline {
    @apply text-gray-500 flex items-center;
}
</style>
