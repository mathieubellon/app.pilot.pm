<template>
<div
    class="Task"
    :class="{
        done: task.done,
        current: task == currentTaskTodo,
    }"
    :id="'LinkedTask-' + task.id"
    v-handle
>
    <template v-if="currentTaskState === TASK_STATES.editName">
        <div class="LinkedTask__name w-full p-3">
            <CharInputWrapping
                v-model="nameEdited"
                class="nameEditionInput my-1 font-semibold"
                ref="nameEditionInput"
                :schema="{ placeholder: $t('taskTitle') }"
            />
            <button
                class="button is-small is-green mr-2 my-1"
                @click.prevent="endNameEdition"
            >
                {{ $t("save") }}
            </button>
            <button
                class="button is-small my-1"
                @click.prevent="cancelNameEdition"
            >
                {{ $t("cancel") }}
            </button>
        </div>
    </template>
    <template v-if="currentTaskState === TASK_STATES.taskIsNotDone">
        <!---->
        <div class="Task__AboveLine">
            <div class="Task__Name">
                <div
                    class="cursor-pointer border-b border-dashed hover:bg-blue-50 hover:border-gray-400"
                    :class="task.done ? 'LinkedTask__name is-done' : 'LinkedTask__name'"
                    @click="startNameEdition"
                >
                    {{ task.name }}
                </div>
                <div
                    v-if="task.name === ''"
                    class="border-b text-gray-400 border-dashed hover:bg-blue-50 hover:border-gray-400"
                    @click="startNameEdition"
                >
                    {{ $t("clickHereToAddName") }}
                </div>
            </div>
            <!--Options-->
            <LinkedTasksOptions
                :isItemTask="isItemTask"
                :namespace="namespace"
                :task="task"
            />
        </div>
        <!--Below line-->
        <div class="Task__BelowLine">
            <div class="flex w-full items-center flex-wrap">
                <!--Mark as done-->
                <div class="mr-1">
                    {{ $t("toBeDoneFor") }}
                </div>
                <!--Deadline-->
                <DatePickerPopper
                    :naiveTime="true"
                    triggerElementName="PopperRef"
                    :value="task.deadline"
                    @input="onDeadlineInput"
                >
                    <template #triggerElement>
                        <a
                            class="actionlink mr-1"
                            :class="{ 'text-red-500': !task.done && isLate }"
                            ref="PopperRef"
                        >
                            <!-- Display late tasks in red -->
                            <BarLoader
                                v-if="
                                    fieldsCurrentlyUpdating.deadline &&
                                    loadingInProgress[`partialUpdateTask${task.id}`]
                                "
                                :key="task.id"
                                :width="50"
                            />
                            <template v-else-if="task.deadline">
                                {{ task.deadline | dateFormat }}
                            </template>
                            <span v-else>{{ $t("selectDate") }}</span>
                        </a>
                    </template>
                    <template #message>
                        <span>{{ $t("deadline") }}</span>
                    </template>
                </DatePickerPopper>

                <!--Assignees-->
                <div class="flex flex-wrap items-center cursor-pointer">
                    <span class="mr-1">{{ $t("by") }}</span>
                    <div
                        v-if="task.assignees.length > 0"
                        class="flex max-w-xs overflow-hidden bg-gray-50 rounded border border-gray-100 leading-tight cursor-pointer hover:bg-blue-50"
                        @click.prevent="pickAssignees()"
                    >
                        <div
                            v-for="assignee in task.assignees.slice(0, 2)"
                            class="mr-1 text-gray-700"
                            :key="assignee.id"
                        >
                            @{{ assignee.username }},
                        </div>
                        <a
                            v-if="task.assignees.length > 2"
                            class="ml-1"
                        >
                            {{ $t("moreAssignees") }}&nbsp;+{{ task.assignees.length - 2 }}
                        </a>
                    </div>

                    <a
                        v-else
                        class="actionlink"
                        @click.prevent="pickAssignees()"
                    >
                        {{ $t("selectAssignees") }}
                    </a>
                </div>
            </div>
            <!--Task is publication-->
            <div class="flex w-full items-center">
                {{ $t("isTaskCompleted") }}
                <BarLoader
                    v-if="
                        fieldsCurrentlyUpdating.done &&
                        loadingInProgress[`partialUpdateTask${task.id}`]
                    "
                    :key="task.id"
                    :width="50"
                />
                <a
                    v-else
                    class="actionlink flex items-center my-1 mx-1"
                    @click.prevent="confirmToggleTaskDone"
                >
                    {{ $t("clickHere") }}
                </a>
            </div>
            <div class="flex w-full flex-wrap">
                <!--Task is publication-->
                <div
                    v-if="task.is_publication && isItemTask"
                    class="cursor-pointer inline-flex items-center text-xs font-semibold text-indigo-800"
                    v-tooltip.top="$t('publicationTaskExplain')"
                >
                    {{ $t("publicationTask") }}
                    <Icon
                        class="fill-current w-4 mx-1"
                        name="QuestionMark"
                    />
                </div>
            </div>
        </div>
    </template>
    <template v-if="currentTaskState === TASK_STATES.taskIsDone">
        <!--Above line-->
        <div class="Task__AboveLine">
            <div class="Task__Name">
                <div
                    class="cursor-pointer LinkedTask__name is-done border-b border-dashed hover:bg-blue-50 hover:border-gray-400"
                >
                    {{ task.name }}
                </div>
            </div>
            <!--Options-->
            <LinkedTasksOptions
                :isItemTask="isItemTask"
                :namespace="namespace"
                :task="task"
            />
        </div>
        <div class="Task__BelowLine">
            <div
                v-if="task.done_by && task.done_at"
                class="mr-3"
            >
                <span>{{ $t("doneBy") }}</span>
                <UserDisplay :user="task.done_by" />
                <span>{{ $t("doneAt") }} {{ task.done_at | dateFormat }}</span>
            </div>
            <div
                v-else
                class="mr-1"
            >
                {{ $t("doneByUnknown") }}
            </div>
            <BarLoader
                v-if="
                    fieldsCurrentlyUpdating.done && loadingInProgress[`partialUpdateTask${task.id}`]
                "
                :key="task.id"
                :width="50"
            />
            <a
                v-else
                class="actionlink text-sm"
                @click.prevent="confirmToggleTaskDone()"
            >
                {{ $t("markTaskAsUndone") }}
            </a>
        </div>
    </template>
    <template v-if="currentTaskState === TASK_STATES.dragging">dragging</template>
    <template v-if="currentTaskState === TASK_STATES.postConfirmationActions">
        <div
            class="bg-white p-5"
            key="nextTaskToDo"
        >
            <div class="font-bold">🎉{{ $t("thisTaskIsMarkedAsDone") }}</div>

            <div class="text-gray-800 my-5 leading-tight">
                <div class="font-medium mb-1">{{ $t("youCanChangeState") }}</div>
                <ItemStateDropdown
                    :inactiveMentionGroups="inactiveMentionGroups"
                    :item="item"
                    referenceClass="p-1 bg-gray-100 border-gray-200"
                    @saved="receiveItem"
                />
            </div>

            <!--UX is not great for this piece of code, commenting because improving it will consume too much time-->
            <!--
                <div class="text-gray-800 my-2 leading-tight"
                     v-if="nextTaskToDo.assignees.length > 0">
                    <div class="font-medium">{{ $t('shouldNotifyAfterDone') }} "{{ nextTaskToDo.name }}" ?</div>
                    <SmartButtonSpinner
                        :successText="$t('notificationDone')"
                        @click="notifyAfterTaskDone"
                        class="button is-small is-blue"
                        name="sendTaskNotification"
                    >
                        {{ $t('yesNotify') }}
                    </SmartButtonSpinner>
                </div>
                -->

            <button
                class="button is-blue is-small"
                @click="showWorkflowScreen = false"
            >
                {{ $t("close") }}
            </button>
        </div>
    </template>
</div>
</template>

<script>
import $ from "jquery"
import moment from "moment"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { required } from "vuelidate/lib/validators"
import PilotMixin from "@components/PilotMixin"
import LinkedTasksStoreMapper from "./LinkedTasksStoreMapper"

import { HandleDirective } from "vue-slicksort"

import CharInputWrapping from "@components/forms/widgets/CharInputWrapping"
import ItemStateDropdown from "@views/items/ItemStateDropdown.vue"
import LinkedTasksOptions from "@views/tasks/linkedTasks/LinkedTasksOptions"

const TASK_STATES = {
    editName: "editName",
    taskIsDone: "taskIsDone",
    taskIsNotDone: "taskIsNotDone",
    confirmToggle: "confirmToggle",
    dragging: "dragging",
    postConfirmationActions: "postConfirmationActions",
}

export default {
    name: "LinkedTaskElement",
    directives: { handle: HandleDirective },
    mixins: [PilotMixin, LinkedTasksStoreMapper],
    components: {
        CharInputWrapping,
        LinkedTasksOptions,
        ItemStateDropdown,
    },
    props: {
        task: Object,
        isItemTask: Boolean,
        inactiveMentionGroups: Object,
    },
    data: () => ({
        toggleTaskDoneRequested: false,
        isNameInEdition: false,
        nameEdited: null,
        nextTaskToDo: null,
        showWorkflowScreen: false,
        TASK_STATES,
    }),
    validations: {
        nameEdited: { required },
    },
    computed: {
        currentTaskState() {
            /* Warning : order in the else if is really important */
            if (this.isNameInEdition) {
                return TASK_STATES.editName
            } else if (this.toggleTaskDoneRequested) {
                return TASK_STATES.confirmToggle
            } else if (this.isItemTask && this.showWorkflowScreen) {
                return TASK_STATES.postConfirmationActions
            } else if (this.task.done) {
                return TASK_STATES.taskIsDone
            } else {
                return TASK_STATES.taskIsNotDone
            }
            /*
nextTaskToDo

            return TASK_STATES.confirmToggle
            return TASK_STATES.dragging
            return TASK_STATES.postConfirmationActions
            */
        },
        ...mapState("users", ["me"]),
        ...mapState("loading", ["loadingInProgress"]),
        ...mapState("itemDetail", ["item"]),
        endOfDayDeadline() {
            return moment(this.task.deadline).add(1, "days")
        },
        isLate() {
            return moment(this.endOfDayDeadline) < moment()
        },
    },
    methods: {
        ...mapActions("itemDetail", ["receiveItem"]),
        startNameEdition() {
            this.nameEdited = this.task.name
            this.isNameInEdition = true
            this.$nextTick(() => {
                $(this.$refs.nameEditionInput.$el).focus()
            })
        },
        endNameEdition() {
            this.partialUpdateTask({
                id: this.task.id,
                name: this.nameEdited,
            }).then(() => (this.isNameInEdition = false))
        },
        cancelNameEdition() {
            this.nameEdited = null
            this.isNameInEdition = false
        },
        pickAssignees() {
            this.setTaskToEdit(this.task)
            this.openOffPanel("taskAssigneesPicker")
        },
        onDeadlineInput(deadline) {
            this.partialUpdateTask({
                id: this.task.id,
                deadline: deadline,
            })
        },
        confirmToggleTaskDone() {
            this.toggleTaskDoneRequested = false

            this.partialUpdateTask({
                id: this.task.id,
                done: !this.task.done,
            }).then((task) => {
                if (task.done) {
                    this.nextTaskToDo = this.getNextTaskToDo(task)
                    this.showWorkflowScreen = true
                }
            })
        },
        cancelToggleTaskDone() {
            this.toggleTaskDoneRequested = false
        },

        notifyAfterTaskDone() {
            this.sendNotification({
                task: this.nextTaskToDo,
                type: "todo",
            })
            this.nextTaskToDo = null
        },
    },
    created() {
        // This should happen during task creation
        if (this.task.name == "") {
            this.startNameEdition()
        }
    },
    i18n: {
        messages: {
            fr: {
                assignees: "Responsables",
                clickHereToAddName: "Cliquez ici pour modifier le nom",
                deadline: "Date de rendu",
                deleteTask: "Supprimer",
                doneAt: "le",
                doneBy: "Marquée comme terminée par",
                doneByUnknown: "Cette tâche a été marquée 'réalisée'",
                isTaskCompleted: "La tâche est terminée ?",
                markTaskAsUndone: "Annuler l'action",
                moreAssignees: "...",
                noThanks: "Non merci",
                notificationDone: "Ok, notifications envoyées",
                open: "Voir la liste",
                publicationTask: "Tâche de publication",
                publicationTaskExplain:
                    "C'est cette tâche qui nous sert de date de publication dans les listes ou calendriers éditoriaux",
                selectAssignees: "choisir responsables",
                selectDate: "choisir date",
                setNameToCreate: "Choisir un nom pour créer",
                shouldNotifyAfterDone:
                    "Souhaitez-vous notifier automatiquement le ou les responsables de la tâche suivante que celle-ci est terminée ?",
                taskDoneClickHere: "Tâche terminée ? Cliquez ici",
                taskTitle: "Intitulé de la tâche",
                thisTaskIsMarkedAsDone: "Bravo, une nouvelle tâche de faite !",
                thisTaskIsTheCurrentOne: "Tâche courante",
                toBeDoneFor: "A faire pour le",
                youCanChangeState: "Changer le statut de workflow du contenu ?",
            },
            en: {
                Assigned: "Assignees",
                clickHereToAddName: "Click here to change the name",
                deadline: "Deadline",
                deleteTask: "Delete",
                doneAt: "at",
                doneBy: "by",
                doneByUnknown: "This task has been marked 'completed'",
                isTaskCompleted: "Is the task complete?",
                markTaskAsUndone: "Undo",
                moreAssigns: "...",
                noThanks: "No thanks.",
                notificationDone: "Ok, notifications sent",
                open: "View list",
                publicationTask: "Publication Task",
                publicationTaskExplain:
                    "It is this task that serves as the date of publication for the content in lists views or editorial calendars",
                selectAssignees: "select assignees",
                selectDate: "choose date",
                setNameToCreate: "Choose a name to create",
                shouldNotifyAfterDone:
                    "Would you like to automatically notify the person(s) responsible for the next task that the task has been completed",
                taskDoneClickHere: "Task completed? Click here",
                taskTitle: "Task Title",
                thisTaskIsMarkedAsDone: "Well done, another task done!",
                thisTaskIsTheCurrentOne: "Current Task",
                toBeDoneFor: "To do for the",
                youCanChangeState: "Changing the workflow status of content...",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

@keyframes TaskColorChange {
    from {
        background-color: #fff;
    }
    to {
        background-color: #9fe6fe;
    }
}

.Task {
    @apply w-full flex bg-white rounded my-2 border border-gray-300 flex flex-col flex-grow w-full;
    cursor: grab;
    min-height: 6em;

    &.twinkle {
        animation: TaskColorChange 0.4s 8 alternate;
    }
}
.Task:active {
    cursor: grabbing;
}

.Task__AboveLine {
    @apply flex items-center w-full;
}

.Task__BelowLine {
    @apply flex flex-wrap px-3 py-1 leading-6 text-sm font-medium text-gray-700;
    a {
        @apply text-blue-500;
    }
}

.Task__Name {
    @apply flex-1 mx-3;
}

.LinkedTask__name {
    @apply text-gray-900 text-gray-900 font-semibold;
}

.LinkedTask__name.is-done {
    @apply text-gray-500 line-through;
}

.LinkedTasks__SortableHelper {
    .Task {
        z-index: 20;
        cursor: grabbing;
        @apply shadow-xl;
        transform: rotate(5deg);
        transition: all 200ms ease-out;
    }
}

.Task.done {
    @apply bg-gray-100;
}

.LinkedTask__Gutter {
    @apply flex items-center flex-shrink-0;
}

.LinkedTask__Main {
    @apply flex flex-grow w-full items-center justify-start;
    // min-height: 150px; // This is for the Spinner
}

.LinkedTask__Options {
    @apply flex items-center p-1;
}

.LinkedTask__MoveHandle {
    cursor: grab;
}
</style>
