<template>
<!--options-->
<div class="LinkedTask__Options cursor-default">
    <!--Manage Reminders-->
    <LinkedRemindersModal
        :objectId="task.id"
        :reminders="task.reminders"
        targetType="task_deadline"
    />

    <Popper
        ref="TaskDropdown"
        placement="bottom"
        triggerElementName="TaskElementPopper"
        triggerType="click"
    >
        <template #triggerElement>
            <a
                class="button is-small is-white text-gray-500 flex-shrink-0"
                :class="{
                    'bg-gray-100 hover:bg-gray-200': task.done,
                }"
                ref="TaskElementPopper"
            >
                <Icon
                    v-if="task.reminders.length > 0"
                    class="mr-2 w-4"
                    name="Bell"
                />
                {{ $t("options") }}
            </a>
        </template>

        <template #content>
            <!--Delete confirm screen-->
            <div
                v-if="deletionRequested"
                class="flex flex-col w-full items-center p-4 my-2 bg-gray-100 rounded max-w-sm"
                key="deletion"
            >
                <div class="font-medium">
                    <div>{{ $t("warningDeleteTask") }}: "{{ task.name }}"</div>
                </div>
                <div
                    v-if="task.assignees.length > 0"
                    class="mt-2 text-center"
                >
                    {{ $t("shouldNotifyAfterDeletion") }}
                    <br />
                    <ToggleButton
                        v-model="shouldNotifyAfterDeletion"
                        class="mt-2"
                        :labels="{ checked: $t('yesNotify'), unchecked: $t('noDontNotify') }"
                        :sync="true"
                        :width="125"
                    />
                </div>

                <div class="mt-6">
                    <SmartButtonSpinner
                        class="button is-small is-red mr-2"
                        :name="'deleteTask' + task.id"
                        @click="confirmDeletion()"
                    >
                        {{ $t("confirmDeletion") }}
                    </SmartButtonSpinner>

                    <button
                        class="button is-small"
                        @click.prevent="deletionRequested = false"
                    >
                        {{ $t("cancel") }}
                    </button>
                </div>
            </div>

            <!--Default Menu-->
            <div
                v-else
                class="max-w-sm"
            >
                <!-- Reminders -->
                <button
                    class="menu-item whitespace-normal"
                    :class="{ disabled: !task.deadline }"
                    @click.prevent="showRemindersModal"
                >
                    <Icon
                        class="w-12 mr-5"
                        name="Bell"
                    />

                    <a
                        v-if="task.reminders.length > 0 && task.deadline"
                        class="actionlink hover:underline is-gray is-small"
                    >
                        {{
                            $tc("youHaveXReminder", task.reminders.length, [task.reminders.length])
                        }}
                    </a>
                    <a
                        v-else-if="task.deadline"
                        class="actionlink"
                    >
                        {{ $t("addReminder") }}
                    </a>
                    <template v-else>
                        {{ $t("addDeadlineForReminder") }}
                    </template>
                </button>

                <!-- Task deletion -->
                <button
                    class="menu-item"
                    :class="{
                        'is-red': task.can_be_hidden,
                        disabled: !task.can_be_hidden,
                    }"
                    @click.prevent="requestDeletion()"
                >
                    <Icon
                        class="w-12 mr-5"
                        name="Trash"
                    />

                    <template v-if="task.can_be_hidden">
                        {{ $t("delete") }}
                    </template>
                    <template v-else>
                        <div class="flex flex-col items-start">
                            <span>{{ $t("taskCannotBeDeleted") }}</span>
                            <span class="menu-item-description">
                                {{ $t("taskCannotBeDeletedExplain") }}
                            </span>
                        </div>
                    </template>
                </button>

                <!-- Is publication task ?-->
                <label
                    v-if="isItemTask"
                    class="menu-item"
                >
                    <ToggleButton
                        class="toggle self-start"
                        :labels="true"
                        :value="task.is_publication"
                        @change="toggleIsPublication"
                    />
                    <div class="flex flex-col items-start">
                        <span>
                            <Loadarium
                                v-if="fieldsCurrentlyUpdating.is_publication"
                                :name="`partialUpdateTask${task.id}`"
                            />
                            <template v-else>{{ $t("setAsPublicationTask") }}</template>
                        </span>
                        <!--Task is publication-->
                        <div
                            v-if="task.is_publication"
                            class="cursor-pointer inline-flex items-center text-xs font-semibold text-indigo-800"
                        >
                            {{ $t("publicationTask") }}
                        </div>
                        <span class="menu-item-description">
                            {{ $t("publicationTaskExplain") }}
                        </span>
                    </div>
                </label>

                <!-- Can be hidden ? -->
                <label class="menu-item">
                    <ToggleButton
                        class="toggle self-start"
                        :labels="true"
                        :value="!task.can_be_hidden"
                        @change="
                            partialUpdateTask({
                                id: task.id,
                                can_be_hidden: !task.can_be_hidden,
                            })
                        "
                    />
                    <div class="flex flex-col items-start">
                        <span>
                            <Loadarium
                                v-if="fieldsCurrentlyUpdating.can_be_hidden"
                                :name="`partialUpdateTask${task.id}`"
                            />
                            <template v-else>{{ $t("ProtectAgainstDeletion") }}</template>
                        </span>
                        <span class="menu-item-description">
                            {{ $t("ProtectAgainstDeletionExplain") }}
                        </span>
                    </div>
                </label>
            </div>
        </template>
    </Popper>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"
import { ToggleButton } from "vue-js-toggle-button"
import LinkedRemindersModal from "@views/notifications/reminder/LinkedRemindersModal.vue"
import LinkedTasksStoreMapper from "./LinkedTasksStoreMapper"

export default {
    name: "LinkedTasksOptions",
    props: {
        task: Object,
        isItemTask: Boolean,
    },
    mixins: [PilotMixin, LinkedTasksStoreMapper],
    components: {
        ToggleButton,
        LinkedRemindersModal,
    },
    data: () => {
        return {
            deletionRequested: false,
            shouldNotifyAfterDeletion: true,
        }
    },
    computed: {
        ...mapState("loading", ["loadingInProgress"]),
        modalName() {},
    },
    methods: {
        showRemindersModal() {
            this.$modal.show(`linkedReminders-${this.task.id}`)
        },
        toggleIsPublication() {
            this.partialUpdateTask({
                id: this.task.id,
                is_publication: !this.task.is_publication,
            })
        },
        requestDeletion() {
            if (this.task.can_be_hidden) {
                this.deletionRequested = true
                this.$refs.TaskDropdown.updatePopper()
            }
        },
        confirmDeletion() {
            this.deleteTask({
                task: this.task,
                notify: this.shouldNotifyAfterDeletion,
            })
        },
    },
    i18n: {
        messages: {
            fr: {
                addDeadlineForReminder:
                    "Impossible de programmer des rappels si la tâche n'a pas de date de livraison",
                noDontNotify: "Non, ne rien faire",
                ProtectAgainstDeletion: "Protéger contre la suppression",
                ProtectAgainstDeletionExplain:
                    "Activez cette option pour signaler aux autres que vous ne voulez pas que cette tâche soit supprimée. Utile pour les tâches importantes par exemple",
                publicationTask: "Tâche de publication",
                publicationTaskExplain:
                    "Sa date de livraison sera la date de publication du contenu et seul ce type de tâche apparait dans les calendriers éditoriaux",
                setAsPublicationTask: "Définir comme tâche de publication",
                shouldNotifyAfterDeletion:
                    "Souhaitez-vous notifier les responsables de la tâche de sa suppression ?",
                showInPublishingCalendar: "Forcer l'affichage en calendrier éditorial",
                showInPublishingCalendarExplain:
                    "Seules les tâches de publication apparaissent dans les calendriers éditoriaux mais en activant cette option vous pouvez forcer cette tâche à y apparaitre",
                taskCannotBeDeleted: "Cette tâche ne peut pas être supprimée",
                taskCannotBeDeletedExplain:
                    "Elle a été protégée contre la suppression, sans doute pour une bonne raison, ça doit être une tâche essentielle au workflow",
                warningDeleteTask: "Attention : Vous allez supprimer définitivement la tâche",
                yesNotify: "Oui, notifier",
            },
            en: {
                addDeadlineForReminder:
                    "Impossible to schedule reminders if the task has no delivery date",
                noDontNotify: "No, do nothing",
                ProtectAgainstDeletion: "Protect against deletion",
                ProtectAgainstDeletionExplain:
                    "Enable this option to tell others that you do not want this task deleted. Useful for important tasks for example",
                publicationTask: "Publication Task",
                publicationTaskExplain:
                    "Its delivery date will be the date of publication of the content and only this type of task appears in the editorial calendars",
                setAsPublicationTask: "Set as publication task",
                shouldNotifyAfterDeletion:
                    "Would you like to notify the task managers of its deletion?",
                showInPublishingCalendar: "Force editorial calendar display",
                showInPublishingCalendarExplain:
                    "Only publication tasks appear in the editorial calendars but by enabling this option you can force this task to appear in the editorial calendars",
                taskCannotBeDeleted: "This task cannot be deleted",
                taskCannotBeDeletedExplain:
                    "It has been protected against deletion, probably for a good reason, it must be an essential task in the workflow",
                warningDeleteTask: "Warning: You will permanently delete the task",
                yesNotify: "Yes, notify",
            },
        },
    },
}
</script>
