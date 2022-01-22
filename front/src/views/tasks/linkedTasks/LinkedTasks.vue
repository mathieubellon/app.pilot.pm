<template>
<div class="LinkedTasks">
    <!--    <Loadarium name="importTaskGroup">
        {{ $t('loading') }}
    </Loadarium>-->
    <SlickList
        v-if="linkedTasks.length > 0"
        class="LinkedTasks__List"
        axis="y"
        :distance="5"
        helperClass="LinkedTasks__SortableHelper"
        lockAxis="y"
        :lockToContainerEdges="true"
        :useDragHandle="true"
        :value="linkedTasks"
        @input="onTasksSorted"
    >
        <transition-group
            name="LinkedTasks__transition"
            enter-active-class="animated fadeIn"
            leave-active-class="animated fadeOut"
        >
            <SlickItem
                v-for="(task, taskIndex) in linkedTasks"
                class="sortable"
                :index="taskIndex"
                :key="task.id"
            >
                <LinkedTasksElement
                    :inactiveMentionGroups="inactiveMentionGroups"
                    :isItemTask="isItemTask"
                    :namespace="namespace"
                    :task="task"
                />
            </SlickItem>
        </transition-group>
    </SlickList>

    <div
        v-else
        class="help-text max-w-lg mx-auto"
    >
        <div class="help-text-title">
            <span>{{ $t("noTasks") }}</span>
        </div>
        <div class="help-text-content">{{ $t("explainTasks") }}</div>
    </div>

    <div
        class="w-full flex max-w-lg flex-row flex-wrap my-6"
        :class="{ 'mx-auto': linkedTasks.length === 0 }"
    >
        <button
            class="button is-blue is-small my-2 mr-3"
            @click.prevent="startTaskCreation()"
        >
            +
            <Icon
                class="text-white"
                name="Check"
            />
            {{ $t("newTask") }}
        </button>

        <Popper
            closeOnClickSelector=".CloseOnClick"
            triggerElementName="PopperRef"
            triggerType="click"
        >
            <template #triggerElement>
                <button
                    class="button is-blue is-small my-2"
                    ref="PopperRef"
                >
                    +
                    <Icon
                        class="fill-current text-white"
                        name="CheckMultiple"
                    />
                    {{ $t("newTasks") }}
                </button>
            </template>

            <template #content>
                <div class="flex flex-col max-w-xs">
                    <div class="text-gray-600 font-medium mb-3">{{ $t("ImportTasksGroup") }}</div>
                    <a
                        v-for="taskGroup in taskGroups"
                        class="button CloseOnClick w-full my-1"
                        v-tooltip="taskGroup.description ? taskGroup.description : 'noDescription'"
                        @click="importTaskGroup(taskGroup)"
                    >
                        + {{ $t("addGroupTasks") }}&nbsp;
                        <Icon
                            class="fill-current w-4"
                            name="CheckMultiple"
                        />
                        &nbsp;"{{ taskGroup.name }}"
                    </a>
                    <div
                        v-if="taskGroups.length == 0"
                        class="button is-white text-gray-600 is-xsmall my-2"
                    >
                        {{ $t("noTasksClickHereToAdd") }}
                    </div>
                    <SmartLink
                        class="actionlink text-sm mt-5"
                        :to="urls.taskGroupApp.url"
                    >
                        {{ $t("manageTasks") }}
                    </SmartLink>
                </div>
            </template>
        </Popper>
    </div>

    <OffPanel name="taskAssigneesPicker">
        <div slot="offPanelTitle">{{ $t("selectAssignees") }}</div>
        <UserPicker
            v-if="taskToEdit"
            slot="offPanelBody"
            :loading="fieldsCurrentlyUpdating.assignees_id"
            :multiple="true"
            :pickedUsersId="taskToEdit.assignees_id"
            :users="choices.users"
            @pick="onAssigneePicked"
        />
    </OffPanel>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { SlickList, SlickItem } from "vue-slicksort"
import PilotMixin from "@components/PilotMixin"
import LinkedTasksStoreMapper from "./LinkedTasksStoreMapper"

import UserPicker from "@components/picker/UserPicker.vue"

import LinkedTasksElement from "./LinkedTasksElement.vue"
import ItemStateDropdown from "@views/items/ItemStateDropdown.vue"

export default {
    name: "LinkedTasks",
    mixins: [PilotMixin, LinkedTasksStoreMapper],
    components: {
        SlickList,
        SlickItem,
        UserPicker,
        LinkedTasksElement,
        ItemStateDropdown,
    },
    props: {
        isItemTask: Boolean,
        inactiveMentionGroups: Object,
    },
    computed: {
        ...mapState("choices", ["choices"]),
        ...mapState("taskGroup", ["taskGroups"]),
        ...mapState("loading", ["loadingInProgress"]),
    },
    methods: {
        ...mapMutations("loading", ["resetLoading"]),
        startTaskCreation() {
            this.createTask({
                name: "",
                order: 0,
            })
        },
        onTasksSorted(newTasks) {
            // Consider the new ordering will be accepted by the backend.
            // This is to prevent the element to flicker when waiting the response from the backend
            this.setLinkedTasks(newTasks)

            // Ask the backend to actually save the new order
            // It will respond with the current state of the label order, which should be the same than ours.
            this.saveCurrentTaskOrder()
        },
        onAssigneePicked(assignees_id) {
            this.partialUpdateTask({
                id: this.taskToEdit.id,
                assignees_id: assignees_id,
            })
        },
    },
    i18n: {
        messages: {
            fr: {
                createTask: "Nouvelle tâche",
                explainTasks:
                    "Les tâches sont utiles pour organiser le travail au sein de l'équipe et recevoir des rappels pour les étapes importantes",
                importFromTaskGroup: "Import groupe de tâche",
                noTasks: "Il n'y a pas de tâche associée à ce projet",
                newTask: "Ajouter une tâche",
                newTasks: "Ajouter plusieurs tâches",
                ImportTasksGroup: "Cliquez sur un de vos groupes de tâches pour les ajouter",
                selectAssignees: "Choisir les responsables",
                manageTasks: "Gérez vos tâches préconfigurées",
                noTasksClickHereToAdd: "Vous n'avez pas de tâches pré-configurées",
                addGroupTasks: "Ajouter le groupe",
            },
            en: {
                createTask: "Create task",
                explainTasks:
                    "Tasks are useful for organizing work within the team and receiving reminders for important steps",
                importFromTaskGroup: "Import task group",
                noTasks: "There are no tasks associated with this project.",
                newTask: "Add a task",
                newTasks: "Add multiple tasks",
                ImportTasksGroup: "Preconfigured task groups",
                selectAssignees: "Select assignees",
                manageTasks: "Manage your pre-configured tasks",
                noTasksClickHereToAdd: "You don't have any pre-configured tasks",
                addGroupTasks: "Add group",
            },
        },
    },
}
</script>

<style lang="scss">
.LinkedTasks {
    @apply flex flex-col;
}

.LinkedTasks__importFromTaskGroupPopper {
    width: 400px;
}
</style>
