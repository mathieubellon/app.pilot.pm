<template>
<div class="ItemAddForm flex flex-col flex-auto">
    <BaseForm
        :errorText="$t('itemCreationError')"
        :model="item"
        :saveUrl="urls.items"
        :stretched="true"
        :successText="$t('itemCreated')"
        :vuelidate="validation"
        @cancel="closeForm"
        @saved="onItemSaved"
    >
        <template #default>
            <ItemContentFormField
                v-if="fieldSchema.show_in_creation"
                v-for="fieldSchema in itemType.content_schema"
                :fieldSchema="fieldSchema"
                :item="item"
                :key="fieldSchema.name"
                :validation="validation"
                :warnings="warnings"
                @addElasticElement="onAddElasticElement"
                @deleteElasticElement="onDeleteElasticElement"
                @input="updateItemFormFieldValue"
            />

            <!-- Language Select ( for translation creation ) -->
            <div
                v-if="currentDesk.itemLanguagesEnabled && isTranslation"
                class="form__field"
            >
                <div class="form__field__label">{{ labels.language }}</div>
                <SelectInput
                    v-model="item.language"
                    :choices="languagesChoices"
                    @input="touch(validation.language)"
                />

                <ValidationErrors :validation="validation.language" />
            </div>

            <a
                class="button w-full"
                type="button"
                @click.prevent="toggleMoreFields()"
            >
                <div
                    v-if="moreFields"
                    class="underline"
                >
                    {{ $t("hideFields") }}
                </div>
                <template v-else>
                    {{ $t("moreFields") }}
                    <span
                        v-if="anyMetadataRequired"
                        class="text-red-600 ml-1"
                    >
                        ({{ $t("metadataFieldsRequired") }})
                    </span>
                </template>
            </a>

            <transition
                enter-active-class="animated fadeIn"
                leave-active-class="animated fadeOut"
            >
                <div
                    v-show="moreFields"
                    class="mt-5"
                >
                    <FormField
                        v-model="item.publication_dt"
                        :schema="{
                            type: 'date',
                            label: labels.publication_dt,
                            naiveTime: true,
                        }"
                        :vuelidate="validation.publication_dt"
                    />

                    <div
                        v-if="workflowStateChoices.length > 0"
                        class="form__field"
                    >
                        <div class="form__field__label">{{ labels.workflowState }}</div>
                        <SelectInput
                            v-model="item.workflow_state_id"
                            :choices="workflowStateChoices"
                            :clearable="false"
                            @input="touch(validation.workflow_state_id)"
                        />
                        <ValidationErrors :validation="validation.workflow_state_id" />
                    </div>

                    <div
                        v-if="taskGroupChoices.length > 0"
                        class="form__field"
                    >
                        <div class="form__field__label">{{ labels.taskGroup }}</div>
                        <SelectInput
                            v-model="item.creation_task_group_id"
                            :choices="taskGroupChoices"
                            @input="touch(validation.creation_task_group_id)"
                        />
                        <ValidationErrors :validation="validation.creation_task_group_id" />
                    </div>

                    <!-- Project Picker -->
                    <div
                        v-if="initialProject"
                        class="form__field"
                    >
                        <div class="form__field__label">{{ labels.project }}</div>
                        {{ initialProject.name }}
                    </div>
                    <div
                        v-else-if="choices.projects.length > 0"
                        class="form__field"
                    >
                        <div class="form__field__label">{{ labels.project }}</div>

                        <template v-if="project">
                            <a
                                class="button tiny"
                                @click="onProjectPicked(project)"
                            >
                                X
                            </a>
                            {{ project.name }}
                        </template>
                        <div>
                            <a @click.prevent="openOffPanel('projectPicker')">
                                {{ $t("selectProject") }}
                            </a>
                        </div>

                        <OffPanel name="projectPicker">
                            <div slot="offPanelTitle">{{ $t("selectProject") }}</div>
                            <ProjectPicker
                                slot="offPanelBody"
                                :pickedProject="project"
                                :projects="choices.projects"
                                @pick="onProjectPicked"
                            />
                        </OffPanel>
                        <ValidationErrors :validation="validation.project_id" />
                    </div>
                    <EmptyRelations
                        v-else
                        type="project"
                    />

                    <!-- Owners Picker -->
                    <div class="form__field">
                        <div class="form__field__label">{{ labels.owners }}</div>

                        <div v-for="owner in sortedOwners">
                            <UserDisplay
                                :user="owner"
                                :withAvatar="true"
                            />
                        </div>
                        <a @click.prevent="openOffPanel('ownerPicker')">
                            {{ $t("selectOwners") }}
                        </a>

                        <OffPanel name="ownerPicker">
                            <div slot="offPanelTitle">{{ $t("selectOwners") }}</div>
                            <UserPicker
                                slot="offPanelBody"
                                :multiple="true"
                                :pickedUsersId="item.owners_id"
                                :users="choices.users"
                                @pick="onOwnerPicked"
                            />
                        </OffPanel>
                        <ValidationErrors :validation="validation.owners_id" />
                    </div>

                    <!-- Channels Picker -->
                    <div
                        v-if="choices.channels.length > 0"
                        class="form__field"
                    >
                        <div class="form__field__label">{{ labels.channel }}</div>

                        <div v-for="pickedChannel in sortedPickedChannels">
                            {{ pickedChannel.name }}
                            <span
                                v-if="pickedChannel.folderPath && pickedChannel.folderPath.length"
                                class="text-sm text-gray-400"
                            >
                                / {{ pickedChannel.folderPath.join(" / ") }}
                            </span>
                        </div>
                        <a
                            v-if="!initialChannel"
                            @click.prevent="openOffPanel('channelPicker')"
                        >
                            {{ $t("selectChannels") }}
                        </a>

                        <OffPanel name="channelPicker">
                            <div slot="offPanelTitle">{{ $t("selectChannels") }}</div>
                            <ChannelPicker
                                slot="offPanelBody"
                                :channels="choices.channels"
                                :pickedChannels="pickedChannels"
                                :withHierarchy="true"
                                @pick="onChannelPicked"
                            />
                        </OffPanel>

                        <!--<SelectInput
                            v-model="item.channels_id"
                            :choices="channelChoices"
                            @input="touch(validation.channels_id)"
                        />-->

                        <ValidationErrors :validation="validation.channels_id" />
                    </div>
                    <EmptyRelations
                        v-else
                        type="channel"
                    />

                    <!-- Targets Picker -->
                    <div
                        v-if="choices.targets.length > 0"
                        class="form__field"
                    >
                        <div class="form__field__label">{{ labels.targets }}</div>

                        <div v-for="target in sortedTargets">
                            {{ target.name }}
                        </div>
                        <a @click.prevent="openOffPanel('targetPicker')">
                            {{ $t("selectTarget") }}
                        </a>

                        <OffPanel name="targetPicker">
                            <div slot="offPanelTitle">{{ $t("selectTarget") }}</div>
                            <TargetPicker
                                slot="offPanelBody"
                                :multiple="true"
                                :pickedTargetsId="item.targets_id"
                                :targets="choices.targets"
                                @pick="onTargetPicked"
                            />
                        </OffPanel>

                        <ValidationErrors :validation="validation.targets_id" />
                    </div>
                    <EmptyRelations
                        v-else
                        type="target"
                    />

                    <!-- Language Select -->
                    <div
                        v-if="currentDesk.itemLanguagesEnabled && !isTranslation"
                        class="form__field"
                    >
                        <div class="form__field__label">{{ labels.language }}</div>
                        <SelectInput
                            v-model="item.language"
                            :choices="languagesChoices"
                            @input="touch(validation.language)"
                        />

                        <ValidationErrors :validation="validation.language" />
                    </div>

                    <div class="form__field">
                        <div class="form__field__label">{{ labels.tags }}</div>

                        <Loadarium name="fetchLabels">
                            <div class="ItemAddForm__tags">
                                <Label
                                    v-for="tag in tags"
                                    :goToListOnClick="false"
                                    :key="tag.id"
                                    :label="tag"
                                />
                            </div>
                        </Loadarium>

                        <LabelSelect
                            :multiple="true"
                            placement="right"
                            :sortable="false"
                            targetType="item_tags"
                            triggerElementName="PopperRef"
                            :value="tags"
                            @input="onTagsInput"
                        >
                            <template #triggerElement>
                                <a ref="PopperRef">
                                    {{ $t("selectTags") }}
                                </a>
                            </template>
                        </LabelSelect>

                        <ValidationErrors :validation="validation.tags_id" />
                    </div>

                    <div
                        v-if="currentDesk.privateItemsEnabled"
                        class="form__field ItemAddForm__is_private"
                    >
                        <input
                            v-model="item.is_private"
                            type="checkbox"
                            @input="touch(validation.is_private)"
                        />

                        <span>
                            <div class="form__field__label">{{ $t("isContentPrivate") }}</div>
                            <div class="form__field__description">
                                {{ $t("isContentPrivateExplanation") }}
                            </div>
                        </span>
                    </div>
                </div>
            </transition>
        </template>

        <template #bottom>
            <UsageLimitAlert usageLimitName="items" />
        </template>
    </BaseForm>
</div>
</template>

<script>
import _ from "lodash"
import Vue from "vue"
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"
import { initialDataPromise } from "@js/bootstrap"
import { createItemValidation, createItemWarnings } from "@js/items/itemsUtils"
import { sortByAlphaString } from "@js/utils.js"
import PilotMixin from "@components/PilotMixin"

import ProjectPicker from "@components/picker/ProjectPicker.vue"
import ChannelPicker from "@components/picker/ChannelPicker.vue"
import TargetPicker from "@components/picker/TargetPicker.vue"
import UserPicker from "@components/picker/UserPicker.vue"
import Label from "@views/labels/Label.vue"
import LabelSelect from "@views/labels/LabelSelect.vue"
import EmptyRelations from "@components/forms/EmptyRelations.vue"
import UsageLimitAlert from "@components/UsageLimitAlert.vue"

import ItemContentFormField from "@views/items/contentForm/ItemContentFormField"

const EMPTY_ITEM = {
    item_type: null,
    content: {},
    publication_dt: null,
    workflow_state_id: null,
    creation_task_group_id: null,
    channels_id: [],
    owners_id: [],
    project_id: null,
    tags_id: [],
    targets_id: [],
    language: "",
    is_private: false,
}

export default {
    name: "ItemAddForm",
    mixins: [PilotMixin],
    components: {
        ItemContentFormField,
        ProjectPicker,
        ChannelPicker,
        TargetPicker,
        UserPicker,
        Label,
        LabelSelect,
        EmptyRelations,
        UsageLimitAlert,
    },
    data: () => ({
        item: EMPTY_ITEM,
        validation: null,
        warnings: null,
        moreFields: window.pilot.desk.creationFormsFieldsVisiblesByDefault,
        pickedChannels: [],
    }),
    props: {
        initialItemData: {
            type: Object,
            default: () => ({}),
        },
        initialProject: Object,
        initialChannel: Object,
        itemType: Object,
        isTranslation: Boolean,
    },
    computed: {
        ...mapState("choices", ["choices"]),
        ...mapState("workflow", ["workflowStates"]),
        ...mapGetters("choices", ["channelChoicesById"]),
        ...mapGetters("choices", ["languagesChoices", "taskGroupChoices", "workflowStateChoices"]),
        labels() {
            let labels = {
                publication_dt: this.$t("publication_dt"),
                workflowState: this.$t("workflowState"),
                taskGroup: this.$t("taskGroup"),
                project: this.$t("project"),
                owners: this.$t("owners"),
                channel: this.$t("channel"),
                tags: this.$t("tags"),
                targets: this.$t("targets"),
                language: this.$t("language"),
            }
            _.forEach(this.itemType.metadata_schema, (schema, fieldName) => {
                if (schema.label) {
                    labels[fieldName] = schema.label
                }
            })
            return labels
        },
        project() {
            return _.find(this.choices.projects, { id: this.item.project_id })
        },
        sortedPickedChannels() {
            let pickedChannels = this.pickedChannels.map((pickedChannel) => ({
                name: this.channelChoicesById[pickedChannel.channelId].name,
                folderPath: pickedChannel.folderPath,
            }))
            return sortByAlphaString(pickedChannels, (pickedChannel) => pickedChannel.name)
        },
        sortedTargets() {
            let targets = this.choices.targets.filter((target) =>
                this.item.targets_id.includes(target.id),
            )
            return sortByAlphaString(targets, (target) => target.name)
        },
        sortedOwners() {
            let owners = this.choices.users.filter((owner) =>
                this.item.owners_id.includes(owner.id),
            )
            return sortByAlphaString(owners, (owner) => owner.username)
        },
        tags() {
            let labels = this.$store.state.labels.labels.item_tags
            return labels ? labels.filter((tag) => this.item.tags_id.includes(tag.id)) : []
        },
        anyMetadataRequired() {
            return _.some(this.itemType.metadata_schema, (fieldSchema) => fieldSchema.required)
        },
    },
    methods: {
        ...mapMutations("offPanel", ["closeOffPanel"]),
        ...mapActions("labels", ["fetchLabels"]),
        toggleMoreFields() {
            this.moreFields = !this.moreFields
        },
        resetItem() {
            // this.initialItemData for item copy
            this.item = _.defaults({}, _.cloneDeep(this.initialItemData), _.cloneDeep(EMPTY_ITEM))
            this.item.item_type_id = this.itemType.id
            this.item.creation_task_group_id = this.itemType.task_group_id
            // this.initialProject for item creation from project detail page
            if (this.initialProject) {
                this.item.project_id = this.initialProject.id
            }
            // this.initialChannel for item creation from channel detail page
            if (this.initialChannel) {
                this.item.channels_id = [this.initialChannel.id]
                this.channels = [this.initialChannel]
            }
            // Use the first workflow state by default
            initialDataPromise.then(() => {
                let firstWorkflowState = this.workflowStates[0]
                if (firstWorkflowState) {
                    this.item.workflow_state_id = firstWorkflowState.id
                }
            })
        },
        updateItemFormFieldValue({ fieldName, value }) {
            Vue.set(this.item.content, fieldName, value)
        },
        onAddElasticElement({ fieldName, value }) {
            Vue.set(this.item.content, fieldName, value)
        },
        onDeleteElasticElement({ fieldName, index }) {
            Vue.delete(this.item.content, `${fieldName}-${index}`)
        },
        onItemSaved(data) {
            this.$emit("saved", data)
        },
        closeForm() {
            this.closeOffPanel("addItemForm")
        },
        onProjectPicked(project) {
            this.item.project_id = project.id == this.item.project_id ? null : project.id
            this.closeOffPanel("projectPicker")
        },
        onOwnerPicked(owners_id) {
            this.item.owners_id = owners_id
            this.touch(this.validation.owners_id)
        },
        onChannelPicked(pickedChannels) {
            this.pickedChannels = pickedChannels
            this.item.channels_id = pickedChannels.map((pc) => pc.channelId)
            this.item.picked_channels = pickedChannels
            this.touch(this.validation.channels_id)
        },
        onTargetPicked(targets_id) {
            this.item.targets_id = targets_id
            this.touch(this.validation.targets_id)
        },
        onTagsInput(tags) {
            this.item.tags_id = tags.map((tag) => tag.id)
            this.touch(this.validation.tags_id)
        },
        /**
         * Touch the vuelidate valiodation object, only if its defined.
         * Prevent exception in the console when the metadata has no validation defined.
         * This is required because of the dynamic nature of the metadata validation.
         */
        touch(validation) {
            return validation && validation.$touch()
        },
    },
    created() {
        this.fetchLabels("item_tags")
        this.resetItem()

        let contentSchemaForCreation = this.itemType.content_schema.filter(
            (schema) => schema.show_in_creation,
        )
        this.validation = createItemValidation(
            contentSchemaForCreation,
            this.itemType.metadata_schema,
            this.item,
        )
        this.warnings = createItemWarnings(contentSchemaForCreation, this.item)
        // Set the initial values
        for (let schema of this.itemType.content_schema) {
            // But only on content values for creation
            // And only if there's not already a value coming from the initialItemData prop
            if (schema.show_in_creation && !this.item.content[schema.name]) {
                Vue.set(this.item.content, schema.name, schema.initial || null)
            }
        }
    },
    beforeDestroy() {
        this.validation.freeMemory()
        this.warnings.freeMemory()
    },
    i18n: {
        messages: {
            fr: {
                isContentPrivate: "Contenu privé ?",
                isContentPrivateExplanation:
                    "Sera seulement visible par vous, les responsables que vous désignerez ou les admins",
                itemCreated: "Contenu créé avec succès",
                itemCreationError: "Erreur, le contenu n'a pas été créé",
                metadataFieldsRequired: "Certains sont obligatoires",
                owners: "Responsables",
                publication_dt: "Date de publication",
                workflowState: "Etat de workflow",
            },
            en: {
                isContentPrivate: "Private content ?",
                isContentPrivateExplanation:
                    "Will only visible to you, the owners you designate or the admins",
                itemCreated: "Item successfully created",
                itemCreationError: "Error, the item was not created",
                metadataFieldsRequired: "Some are required",
                owners: "Owners",
                publication_dt: "Publication date",
                workflowState: "Workflow state",
            },
        },
    },
}
</script>

<style lang="scss">
.ItemAddForm__is_private {
    display: flex;
    align-items: center;
    input {
        margin-right: 1em;
    }
}

.ItemAddForm__tags {
    display: flex;
    flex-direction: row;
    flex-flow: wrap;

    .Label {
        margin-right: 5px;
        margin-bottom: 5px;
    }
}
</style>
