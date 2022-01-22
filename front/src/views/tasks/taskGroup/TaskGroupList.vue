<template>
<div>
    <div class="p-5 mb-4 bg-gray-50 border-l-2 border-blue-500 text-gray-700">
        <div class="font-bold">{{ $t("information") }}</div>
        <div>{{ $t("explainTasksGroups") }}</div>
    </div>

    <Loadarium name="fetchTaskGroups">
        <AdminList
            :instancesList="sortedTaskGroups"
            :showActions="myPermissions.is_admin"
            :sortable="false"
            @delete="deleteTaskGroup"
            @edit="goToTaskGroupEdition"
        >
            <div
                class="flex flex-col"
                slot-scope="{ instance }"
            >
                <span class="font-bold">
                    {{ instance.name }}
                </span>

                <span class="text-gray-700">
                    {{ instance.description }}
                </span>

                <a
                    v-if="!myPermissions.is_admin"
                    @click="goToTaskGroupEdition(instance)"
                >
                    {{ $t("details") }}
                </a>
            </div>
        </AdminList>

        <div
            v-if="taskGroups.length === 0"
            class="help-text"
        >
            <div class="help-text-title">{{ $t("taskGroupEmpty") }}</div>
            <button
                class="button is-blue"
                @click="$refs.form.openFormPanel()"
            >
                {{ $t("createTaskGroup") }}
            </button>
        </div>
    </Loadarium>

    <AutoFormInPanel
        name="taskGroupForm"
        ref="form"
        :saveUrl="urls.tasksGroups"
        :schema="taskGroupFormSchema"
        :title="$t('createTaskGroup')"
        @created="appendToTaskGroups"
    />
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import i18n from "@js/i18n"
import { sortByAlphaString } from "@js/utils.js"
import PilotMixin from "@components/PilotMixin"

import AdminList from "@components/admin/AdminList.vue"

export const taskGroupFormSchema = [
    {
        name: "name",
        type: "char",
        label: i18n.t("name"),
        placeholder: i18n.t("name"),
        required: true,
    },
    {
        name: "description",
        type: "text",
        label: i18n.t("description"),
        placeholder: i18n.t("description"),
    },
]

export default {
    name: "TaskGroupList",
    mixins: [PilotMixin],
    components: {
        AdminList,
    },
    data: () => ({
        taskGroupFormSchema,
    }),
    computed: {
        ...mapState("taskGroup", ["taskGroups"]),
        ...mapGetters("users", ["myPermissions"]),
        sortedTaskGroups() {
            return sortByAlphaString(this.taskGroups, (taskGroup) => taskGroup.name)
        },
    },
    methods: {
        ...mapMutations("taskGroup", ["appendToTaskGroups"]),
        ...mapActions("taskGroup", ["deleteTaskGroup"]),
        goToTaskGroupEdition(taskGroup) {
            this.$router.push({ name: "taskGroupDetails", params: { id: taskGroup.id } })
        },
    },
    i18n: {
        messages: {
            fr: {
                createTaskGroup: "Créer un groupe de tâches",
                explainTasksGroups:
                    "Si vous vous retrouvez dans la situation où vous crééz systématiquement les mêmes tâches avec les mêmes responsables pour un ou plusieurs types de contenus les groupes de tâches sont un gain de temps significatif. Pré-configurez une groupe puis importez le en un clic dans votre contenu.",
                manage: "Gérer",
                taskGroupEmpty: "Vous n'avez pas encore créé de groupe de tâches",
            },
            en: {
                createTaskGroup: "Create a task group",
                explainTasksGroups:
                    "If you find yourself in the situation where you systematically create the same tasks with the same owners for one or more types of content, the task groups are a significant time saving. Pre-configure a group and then import it into your content with a single click.",
                manage: "Configure",
                taskGroupEmpty: "You haven't created any task group yet",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";
@import "~@sass/mixins.scss";

.TaskGroupList__content {
    display: flex;
    justify-content: space-between;
    white-space: nowrap;

    cursor: pointer;

    &:hover .TaskGroupList__name {
        text-decoration: underline;
    }
}

.TaskGroupList__name {
    flex-grow: 1;
    font-weight: bold;
}

.TaskGroupList__description {
    font-size: 0.9em;
    color: $gray;
    margin-left: 20px;
    width: 400px;
    @include text-overflow;
}
</style>
