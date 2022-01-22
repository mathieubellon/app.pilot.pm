<template>
<div class="ProjectFormAdd flex flex-col flex-auto">
    <BaseForm
        v-if="!usageLimitReached('projects')"
        :errorText="$t('projectCreationError')"
        :model="model"
        :saveUrl="urls.projects"
        :stretched="true"
        :successText="$t('projectCreated')"
        :vuelidate="$v.model"
        @cancel="closeForm"
        @saved="onProjectSaved"
    >
        <template #default>
            <FormField
                :schema="{
                    type: 'char',
                    label: $t('projectName'),
                    placeholder: $t('projectName'),
                }"
                v-model.trim="model.name"
                :vuelidate="$v.model.name"
            />

            <button
                class="button w-full"
                type="button"
                @click.prevent="toggleMoreFields()"
            >
                <template v-if="moreFields">{{ $t("hideFields") }}</template>
                <template v-else>{{ $t("moreFields") }}</template>
            </button>

            <transition
                enter-active-class="animated fadeIn"
                leave-active-class="animated fadeOut"
            >
                <div
                    v-show="moreFields"
                    class="mt-5"
                >
                    <FormField
                        v-model="model.owners_id"
                        :schema="{
                            type: 'choice',
                            label: $t('owners'),
                            choices: usersChoices,
                            multiple: true,
                        }"
                    />

                    <FormField
                        v-model="model.description"
                        :schema="{
                            type: 'richText',
                            label: $t('description'),
                        }"
                    />

                    <FormField
                        v-model="model.start"
                        :schema="{
                            type: 'date',
                            label: $t('start'),
                            formatWithoutTime: true,
                        }"
                    />

                    <FormField
                        v-model="model.end"
                        :schema="{
                            type: 'date',
                            label: $t('end'),
                            formatWithoutTime: true,
                        }"
                    />

                    <div class="form__field">
                        <label>
                            <div class="form__field__label">{{ $t("files") }}</div>
                            <AssetUploader
                                v-model="model.assets"
                                ref="AssetUploader"
                                @input="$v.model.assets.$touch()"
                                @uploadInProgress="$v.model.assets.$touch()"
                            />
                        </label>
                    </div>

                    <div class="form__field">
                        <div class="form__field__label">{{ $t("category") }}</div>

                        <Loadarium name="fetchLabels">
                            <div class="ItemAddForm__tags">
                                <Label
                                    :goToListOnClick="false"
                                    :label="category"
                                />
                            </div>
                        </Loadarium>

                        <LabelSelect
                            :multiple="false"
                            placement="right"
                            targetType="project_category"
                            triggerElementName="CategoryPopper"
                            :value="category"
                            @input="onCategoryInput"
                        >
                            <template #triggerElement>
                                <a ref="CategoryPopper">
                                    {{ $t("selectCategory") }}
                                </a>
                            </template>
                        </LabelSelect>
                    </div>

                    <div class="form__field">
                        <div class="form__field__label">{{ $t("priority") }}</div>

                        <Loadarium name="fetchLabels">
                            <div class="ItemAddForm__tags">
                                <Label
                                    :goToListOnClick="false"
                                    :label="priority"
                                />
                            </div>
                        </Loadarium>

                        <LabelSelect
                            :multiple="false"
                            placement="right"
                            targetType="project_priority"
                            triggerElementName="PriorityPopper"
                            :value="priority"
                            @input="onPriorityInput"
                        >
                            <template #triggerElement>
                                <a ref="PriorityPopper">
                                    {{ $t("selectPriority") }}
                                </a>
                            </template>
                        </LabelSelect>
                    </div>
                </div>
            </transition>
        </template>

        <template #bottom>
            <UsageLimitAlert usageLimitName="projects" />
        </template>
    </BaseForm>
</div>
</template>

<script>
import { mapGetters, mapMutations, mapActions } from "vuex"
import { required } from "vuelidate/lib/validators"
import { EVENTS, dispatchEvent } from "@js/events"
import PilotMixin from "@components/PilotMixin"

import AssetUploader from "@components/forms/widgets/AssetUploader"
import UsageLimitAlert from "@components/UsageLimitAlert.vue"
import Label from "@views/labels/Label.vue"
import LabelSelect from "@views/labels/LabelSelect.vue"

const isNotUploading = function () {
    if (!this.$refs.AssetUploader) return false
    return !this.$refs.AssetUploader.uploadInProgress
}

export default {
    name: "ProjectFormAdd",
    mixins: [PilotMixin],
    components: {
        AssetUploader,
        UsageLimitAlert,
        Label,
        LabelSelect,
    },
    props: {
        projectListState: String,
        offPanelName: String,
    },
    data() {
        return {
            moreFields: window.pilot.desk.creationFormsFieldsVisiblesByDefault,
            model: {
                name: "",
                owners_id: [],
                description: {},
                start: null,
                end: null,
                assets: [],
                category_id: null,
                priority_id: null,
                state: this.projectListState,
            },
        }
    },
    validations: {
        model: {
            name: { required },
            assets: { isNotUploading },
        },
    },
    computed: {
        ...mapGetters("choices", ["usersChoices"]),
        ...mapGetters("usageLimits", ["usageLimitReached"]),
        category() {
            let labels = this.$store.state.labels.labels.project_category
            return labels ? labels.find((category) => category.id == this.model.category_id) : null
        },
        priority() {
            let labels = this.$store.state.labels.labels.project_priority
            return labels ? labels.find((priority) => priority.id == this.model.priority_id) : null
        },
    },
    methods: {
        ...mapMutations("offPanel", ["closeOffPanel"]),
        ...mapMutations("usageLimits", ["incrementUsage"]),
        toggleMoreFields() {
            this.moreFields = !this.moreFields
        },
        onCategoryInput(category) {
            this.model.category_id = category.id
        },
        onPriorityInput(priority) {
            this.model.priority_id = priority.id
        },
        onProjectSaved(project) {
            dispatchEvent(EVENTS.projectCreated, project)

            setTimeout(() => {
                this.closeForm()
            }, 1000)
        },
        closeForm() {
            this.closeOffPanel(this.offPanelName)
        },
    },
    i18n: {
        messages: {
            fr: {
                files: "Fichiers liés",
                projectCreated: "Projet créé avec succès",
                projectCreationError: "Erreur, le projet n'a pas été créé",
                projectName: "Nom du projet",
                selectCategory: "Sélection catégorie",
                selectPriority: "Sélection priorité",
            },
            en: {
                files: "Linked files",
                projectCreated: "Project successfully created",
                projectCreationError: "Error, the project was not created",
                projectName: "Project Name",
                selectCategory: "Select category",
                selectPriority: "Select priority",
            },
        },
    },
}
</script>
