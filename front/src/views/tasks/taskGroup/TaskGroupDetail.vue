<template>
<div>
    <router-link :to="{ name: 'taskGroupList' }">< {{ $t("back") }}</router-link>

    <div
        v-if="myPermissions.is_admin"
        class="simple-panel my-4 mx-0"
    >
        <AutoForm
            :disableIfUnchanged="true"
            :initialData="currentTaskGroup"
            :saveUrl="urls.tasksGroups"
            :schema="taskGroupFormSchema"
            :showCancel="false"
            @saved="updateTaskGroup"
        />
    </div>

    <div class="flex justify-end mb-4">
        <AdminButton @click="startTaskTemplateCreation()">
            {{ $t("createTask") }}
        </AdminButton>
    </div>

    <AdminList
        :instancesList="currentTaskGroup.tasks"
        :sortable="true"
        @delete="deleteTaskTemplate"
        @edit="$refs.form.openFormPanel($event)"
        @sorted="onTaskTemplatesSorted"
    >
        <div
            class="TaskGroupDetail__content"
            slot-scope="{ instance }"
        >
            <span class="TaskGroupDetail__name">
                {{ instance.name }}
            </span>

            <span class="TaskGroupDetail__flags">
                <span :class="{ active: instance.is_publication }">
                    {{ $t("publication") }} : {{ instance.is_publication | yesno }}
                </span>
                <span :class="{ active: instance.can_be_hidden }">
                    {{ $t("deletion") }} : {{ instance.can_be_hidden | yesno }}
                </span>

                <div>
                    {{ $t("defaultAssignees") }} :
                    <UserDisplay
                        v-for="assignee in instance.assignees"
                        :key="assignee.id"
                        :user="assignee"
                    />
                </div>
            </span>
        </div>
    </AdminList>

    <div
        v-if="currentTaskGroup.tasks.length === 0"
        class="help-text"
    >
        <div class="help-text-title">{{ $t("tasksEmpty") }}</div>
    </div>

    <AutoFormInPanel
        name="taskTemplateForm"
        ref="form"
        :saveUrl="urls.tasksTemplates"
        :schema="taskTemplateFormSchema"
        :title="$t('createTask')"
        @created="appendTaskTemplate"
        @updated="updateTaskTemplate"
    />
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"
import { taskGroupFormSchema } from "./TaskGroupList.vue"

import AdminButton from "@components/admin/AdminButton"
import AdminList from "@components/admin/AdminList.vue"

export default {
    name: "TaskGroupDetail",
    mixins: [PilotMixin],
    components: {
        AdminButton,
        AdminList,
    },
    data: () => ({
        taskGroupFormSchema,
    }),
    computed: {
        ...mapState("taskGroup", ["currentTaskGroup"]),
        ...mapGetters("choices", ["usersChoices"]),
        ...mapGetters("users", ["myPermissions"]),
        taskTemplateFormSchema() {
            return [
                {
                    name: "name",
                    type: "char",
                    label: this.$t("name"),
                    placeholder: this.$t("name"),
                    required: true,
                },
                {
                    name: "assignees_id",
                    type: "choice",
                    choices: this.usersChoices,
                    multiple: true,
                    label: this.$t("defaultAssignees"),
                },
                {
                    name: "is_publication",
                    type: "checkbox",
                    label: this.$t("isPublicationTask"),
                },
                {
                    name: "can_be_hidden",
                    type: "checkbox",
                    label: this.$t("deletableTask"),
                },
            ]
        },
    },
    methods: {
        ...mapMutations("taskGroup", [
            "setTaskTemplates",
            "appendTaskTemplate",
            "updateTaskTemplate",
            "updateTaskGroup",
        ]),
        ...mapActions("taskGroup", ["setTaskTemplatesOrder", "deleteTaskTemplate"]),
        startTaskTemplateCreation() {
            this.$refs.form.openFormPanel({
                task_group_id: this.currentTaskGroup.id,
                assignees_id: [],
                order: this.currentTaskGroup.tasks.length,
                can_be_hidden: true,
            })
        },
        onTaskTemplatesSorted(newTaskTemplates) {
            let newTaskTemplatesOrder = newTaskTemplates.map((taskTemplate, index) => ({
                id: taskTemplate.id,
                order: index,
            }))

            // Consider the new ordering will be accepted by the backend.
            // This is to prevent the element to flicker when waiting the response from the backend
            this.setTaskTemplates(newTaskTemplates)

            // Ask the backend to actually save the new order
            // It will respond with the current state of the label order, which should be the same than ours.
            this.setTaskTemplatesOrder(newTaskTemplatesOrder)
        },
    },
    i18n: {
        messages: {
            fr: {
                createTask: "Ajouter une tâche",
                defaultAssignees: "Responsables par défaut",
                deletion: "Suppression",
                deletableTask: "La tâche peut être supprimée",
                isPublicationTask:
                    "Il s'agit de la tâche de publication (une seule possible par groupe de tâche)",
                publication: "Publication",
                publishingCalendar: "Calendrier publication",
                showInPublishingCalendar: "Apparait dans le calendrier de publication",
                tasksEmpty: "Vous n'avez pas encore créé de tâche dans ce groupe",
            },
            en: {
                createTask: "Add a task",
                defaultAssignees: "Default assignees",
                deletion: "Deletion",
                deletableTask: "Task can be deleted",
                isPublicationTask:
                    "This is the publication task ( only one allowed by task group )",
                publication: "Publication",
                publishingCalendar: "Publishing calendar",
                showInPublishingCalendar: "Appear in the publishing calendar",
                tasksEmpty: "You haven't created any task in this group yet",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.TaskGroupDetail__content {
    display: flex;
    justify-content: space-between;
}

.TaskGroupDetail__name {
    flex-grow: 1;
    font-weight: bold;
    display: flex;
    flex-direction: row;
    align-items: center;
}

.TaskGroupDetail__flags {
    font-size: 0.9em;
    color: $gray;
    margin-left: 20px;
    width: 300px;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;

    & > span {
        color: $red;
    }
    & > span.active {
        color: $green;
    }
}
</style>
