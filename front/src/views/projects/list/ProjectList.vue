<template>
<div class="ProjectList">
    <BigFilter
        :apiSource="apiSource"
        filterSchemaUrl="/api/big_filter/schema/projects/list/"
        :placeholder="$t('projectBigFilterPlaceholder')"
    />

    <div
        v-if="projects.length > 0 && !loadingInProgress.fetchProjectList"
        class="flex flex-grow justify-end"
    >
        <OrderingSelector
            defaultOrdering="-updated_at"
            :orderings="orderings"
            :value="apiSource.ordering"
            @orderingChange="apiSource.setOrdering"
        />
        <Pagination
            class="ml-2"
            :pagination="pagination"
            @pageChange="apiSource.setPage"
        />
    </div>

    <div class="my-5">
        <Loadarium name="fetchProjectList" />

        <template v-if="!loadingInProgress.fetchProjectList">
            <ProjectListElement
                v-for="project in projects"
                :key="project.id"
                :project="project"
            />
        </template>

        <template v-if="projects.length == 0 && !loadingInProgress.fetchProjectList">
            <div
                v-if="apiSource.hasFilter"
                class="text-gray-800 font-bold text-center p-10 bg-gray-50 rounded"
            >
                {{ $t("noResults") }}
            </div>
            <ProjectHelpText v-else />
        </template>
    </div>

    <div
        v-if="projects.length > 0 && !loadingInProgress.fetchProjectList"
        class="flex flex-grow justify-end"
    >
        <Pagination
            :pagination="pagination"
            @pageChange="apiSource.setPage"
        />
    </div>

    <OffPanel
        name="addActiveProjectForm"
        :stretched="true"
    >
        <div slot="offPanelTitle">{{ $t("newProject") }}</div>
        <ProjectFormAdd
            slot="offPanelBody"
            offPanelName="addActiveProjectForm"
            projectListState="active"
        />
    </OffPanel>
    <OffPanel
        name="addIdeaProjectForm"
        :stretched="true"
    >
        <div slot="offPanelTitle">{{ $t("newDraft") }}</div>
        <ProjectFormAdd
            slot="offPanelBody"
            offPanelName="addIdeaProjectForm"
            projectListState="idea"
        />
    </OffPanel>
</div>
</template>

<script>
import { mapState, mapMutations, mapActions, mapGetters } from "vuex"
import PilotMixin from "@components/PilotMixin"

import BigFilter from "@views/bigFilter/BigFilter"
import OrderingSelector from "@views/bigFilter/OrderingSelector"
import Pagination from "@components/Pagination"
import ProjectListElement from "./ProjectListElement"
import ProjectHelpText from "./ProjectHelpText"
import ProjectFormAdd from "./ProjectFormAdd"

export default {
    name: "ProjectList",
    mixins: [PilotMixin],
    components: {
        BigFilter,
        OrderingSelector,
        Pagination,
        ProjectListElement,
        ProjectHelpText,
        ProjectFormAdd,
    },
    computed: {
        ...mapState("projectList", ["projects", "pagination", "apiSource"]),
        ...mapState("loading", ["loadingInProgress"]),
        orderings() {
            return [
                { value: "start", label: this.$t("sortByStartDateOldestFirst") },
                { value: "-start", label: this.$t("sortByStartDateNewestFirst") },
                { value: "name", label: this.$t("sortBYNameAlpha") },
                { value: "-name", label: this.$t("sortByNameAlphaReverse") },
                { value: "created_at", label: this.$t("sortByCreationDateOldestFirst") },
                { value: "-updated_at", label: this.$t("sortByCreationDateNewestFirst") },
                { value: "priority", label: this.$t("sortByPriorityHighestFirst") },
                { value: "-priority", label: this.$t("sortByPriorityLowestFirst") },
            ]
        },
    },
    methods: {
        ...mapActions("projectList", ["fetchProjectList"]),
    },
    watch: {
        "apiSource.url"() {
            this.fetchProjectList()
        },
    },
    created() {
        this.fetchProjectList()
    },
    i18n: {
        messages: {
            fr: {
                newDraft: "Nouvelle proposition",
                projectBigFilterPlaceholder: "Rechercher dans les projets",
                sortByCreationDateNewestFirst: "Date de création, plus récente en premier",
                sortByCreationDateOldestFirst: "Date de création, plus ancienne en premier",
                sortBYNameAlpha: "Nom, A->Z",
                sortByNameAlphaReverse: "Nom, Z->A",
                sortByPriorityHighestFirst: "Priorité, plus élevée en premier",
                sortByPriorityLowestFirst: "Priorité, moins élevée en premier",
                sortByStartDateNewestFirst: "Date de début, plus récente en premier",
                sortByStartDateOldestFirst: "Date de début, plus ancienne en premier",
            },
            en: {
                newDraft: "New suggestion",
                projectBigFilterPlaceholder: "Search the projects",
                sortByCreationDateNewestFirst: "Creation date, newest first",
                sortByCreationDateOldestFirst: "Creation date, oldest first",
                sortBYNameAlpha: "Name, A->Z",
                sortByNameAlphaReverse: "Name, Z->A",
                sortByPriorityHighestFirst: "Priority, highest first",
                sortByPriorityLowestFirst: "Priority, lowest first",
                sortByStartDateNewestFirst: "Start date, newest first",
                sortByStartDateOldestFirst: "Start date, oldest first",
            },
        },
    },
}
</script>
