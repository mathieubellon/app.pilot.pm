<template>
<div class="ProjectPicker">
    <div class="flex items-center">
        <VueFuse
            class="flex-grow"
            :defaultAll="true"
            :keys="['name']"
            :list="projects"
            :placeholder="$t('search')"
            :threshold="0.1"
            @result="onFuseResult"
        />
        <template v-if="multiple">
            <ButtonSpinner
                class="button is-small is-outlined mx-2"
                :disabled="pickedProjectsId.length == projects.length"
                :isLoading="loading && lastSelection == 'pickAll'"
                @click="pickAll"
            >
                {{ $t("selectAll") }}
            </ButtonSpinner>

            <ButtonSpinner
                class="button is-small is-outlined"
                :disabled="pickedProjectsId.length == 0"
                :isLoading="loading && lastSelection == 'unpickAll'"
                @click="unpickAll"
            >
                {{ $t("deselectAll") }}
            </ButtonSpinner>
        </template>
    </div>

    <div class="Picker__List">
        <div
            v-for="project in filteredProjects"
            class="Picker__ElementWrapper"
        >
            <div
                v-if="loading && lastSelection == project"
                class="Picker__Loader"
            >
                <BarLoader
                    color="#3182CE"
                    :loading="true"
                    :width="100"
                    widthUnit="%"
                />
            </div>
            <ProjectPickerElement
                v-else
                :disabled="loading"
                :key="project.id"
                :picked="isPicked(project)"
                :project="project"
                @pick="onPick"
            />
        </div>
    </div>

    <div
        v-if="projects.length == 0"
        class="help-text"
    >
        <div class="help-text-title">
            <Icon
                class="help-text-icon"
                name="Project"
            />
            <span>{{ $t("noProjectYet") }}</span>
        </div>
        <SmartLink
            class="button is-blue"
            :to="urls.projectsApp.url"
        >
            {{ $t("createProject") }}
        </SmartLink>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import PilotMixin from "@components/PilotMixin"

import ProjectPickerElement from "./ProjectPickerElement.vue"
import ButtonSpinner from "@components/ButtonSpinner"

export default {
    name: "ProjectPicker",
    mixins: [PilotMixin],
    components: {
        ProjectPickerElement,
        ButtonSpinner,
    },
    props: {
        multiple: Boolean,
        projects: Array,
        pickedProject: Object,
        pickedProjectsId: Array,
        loading: Boolean,
    },
    data: () => ({
        filteredProjects: [],
        lastSelection: null,
    }),
    methods: {
        onFuseResult(filteredProjects) {
            this.filteredProjects = filteredProjects
        },
        onPick(project) {
            this.lastSelection = project
            if (this.multiple) {
                // Toggle value in array (https://gist.github.com/uhtred/ec64752a8e9c9b83922b3ebb36e3ac23)
                this.$emit("pick", _.xor(this.pickedProjectsId, [project.id]))
            } else {
                this.$emit("pick", project)
            }
        },
        pickAll() {
            this.lastSelection = "pickAll"
            this.$emit(
                "pick",
                this.projects.map((project) => project.id),
            )
        },
        unpickAll() {
            this.lastSelection = "unpickAll"
            this.$emit("pick", [])
        },
        isPicked(project) {
            if (this.multiple) {
                return _.includes(this.pickedProjectsId, project.id)
            } else {
                return this.pickedProject && this.pickedProject.id == project.id
            }
        },
    },
    i18n: {
        messages: {
            fr: {
                createProject: "Créer un projet",
                noProjectYet: "Vous n'avez pas encore créé de projet",
            },
            en: {
                createProject: "Create a project",
                noProjectYet: "You haven't created any project yet",
            },
        },
    },
}
</script>
