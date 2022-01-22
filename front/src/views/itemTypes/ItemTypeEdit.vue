<template>
<div>
    <SmartLink :to="urls.itemTypesApp.url">< {{ $t("back") }}</SmartLink>

    <Loadarium :name="['fetchContentFieldSpecs', 'fetchItemTypes']">
        <div
            v-if="myPermissions.is_admin"
            class="simple-panel my-4 mx-0"
        >
            <AutoForm
                :disableIfUnchanged="true"
                :initialData="itemType"
                :saveUrl="urls.itemTypes"
                :schema="itemTypeFormSchema"
                :showCancel="false"
                @saved="onFormSaved"
            />
        </div>

        <div>
            <div
                v-if="
                    loadingInProgress.partialUpdateItemType || loadingStatus.partialUpdateItemType
                "
            >
                <div class="ItemSaveLoadingBackdrop" />
                <div class="ItemSaveLoadingMessage">
                    <template v-if="loadingInProgress.partialUpdateItemType">
                        {{ $t("saveItemInProgress") }}
                    </template>
                    <template v-if="loadingStatus.partialUpdateItemType == 'success'">
                        ✅&nbsp;{{ $t("saveItemTypeOk") }}
                    </template>
                    <template v-if="loadingStatus.partialUpdateItemType == 'error'">
                        {{ $t("saveItemTypeError") }} :
                        <br />
                        {{ getErrorMessage("saveItemType") }}
                    </template>
                </div>
            </div>
            <div class="flex container justify-end">
                <a
                    class="flex button mb-4 mr-2"
                    @click="toggleFieldPreview()"
                >
                    {{ $t("previewFields") }}
                </a>
                <AdminButton
                    class="flex button border-none mb-4 is-blue"
                    @click="startFieldSchemaAdd()"
                >
                    {{ $t("add") }}
                </AdminButton>
            </div>

            <SlickList
                v-model="itemType.content_schema"
                axis="y"
                :distance="5"
                helperClass="ItemTypeEditApp__SortableHelper"
                lockAxis="y"
                :lockToContainerEdges="true"
                @input="onContentSchemaSorted"
            >
                <SlickItem
                    v-for="(fieldSchema, fieldSchemaIndex) in itemType.content_schema"
                    class="flex flex-col"
                    :index="fieldSchemaIndex"
                    :key="fieldSchema.name"
                >
                    <div class="flex flex-col mb-2 bg-white border border-gray-200 p-3 rounded">
                        <div class="flex flex-grow items-center justify-between">
                            <div class="flex flex-grow items-center">
                                <a class="button ItemTypeEditApp__dragHandle">
                                    <Icon name="MoveHandle" />
                                </a>
                                <div>
                                    <div class="font-bold text-normal text-purple-700">
                                        {{ fieldSchema.label }}
                                    </div>
                                    <div class="font-semibold text-sm text-gray-500">
                                        {{ getFieldHumanName(fieldSchema) }}
                                    </div>
                                </div>
                            </div>
                            <div class="flex">
                                <AdminButton
                                    aClass="button text-blue-600 mr-2 sm:ml-4"
                                    @click="startFieldSchemaEdition(fieldSchema, fieldSchemaIndex)"
                                >
                                    {{ $t("edit") }}
                                </AdminButton>
                                <AdminButton
                                    v-if="fieldSchema.name != 'title'"
                                    aClass="button text-gray-500"
                                    @click="requestFieldSchemaDeletion(fieldSchema)"
                                >
                                    {{ $t("delete") }}
                                </AdminButton>
                            </div>
                        </div>
                        <div class="ItemTypeEditApp__DragHelpText">
                            <div class="text-gray-600 text-sm">
                                {{ $t("dragHelpText") }}
                            </div>
                        </div>
                        <div class="flex items-center">
                            <div
                                v-if="fieldSchemaDeletionRequested === fieldSchema"
                                class="flex flex-col flex-grow text-red-700 bg-red-100 border border-red-300 p-4 rounded"
                            >
                                {{ $t("fieldDeletionWarning") }}
                                <br />
                                {{ $t("deleteField") }} "{{ fieldSchema.label }}" (
                                {{
                                    $tc("linkedItemsCount", itemType.linked_item_count, {
                                        linkedItemsCount: itemType.linked_item_count,
                                    })
                                }}
                                ) ?
                                <button
                                    class="button is-red mb-1 mt-4"
                                    @click="confirmFieldSchemaDeletion()"
                                >
                                    {{ $t("confirmDeletion") }}
                                </button>
                                <button
                                    class="button"
                                    @click="cancelFieldSchemaDeletion()"
                                >
                                    {{ $t("cancel") }}
                                </button>
                            </div>
                            <div
                                v-if="fieldPreview"
                                class="flex flex-grow border border-gray-300 mt-3 rounded p-3"
                            >
                                <ItemContentFormField
                                    class="w-full"
                                    :fieldSchema="fieldSchema"
                                    :item="fakeItemContentModel"
                                    :validation="fakeItemValidation"
                                    :warnings="fakeItemWarnings"
                                    @input="updateItemFormFieldValue"
                                />
                            </div>
                        </div>
                    </div>
                </SlickItem>
            </SlickList>
        </div>
    </Loadarium>

    <OffPanel
        name="selectFieldSchemaType"
        width="65%"
    >
        <div slot="offPanelTitle">{{ $t("selectFieldSchemaType") }}</div>
        <div slot="offPanelBody">
            <div
                v-for="contentFieldsSpec in contentFieldSpecs"
                class="flex border border-gray-300 p-3 rounded mb-2"
            >
                <div class="flex flex-shrink-0 w-32 justify-center items-center">
                    <ItemContentFieldIcon
                        class="text-gray-600"
                        :name="contentFieldsSpec.type"
                    />
                </div>
                <div class="flex-grow">
                    <div class="font-bold">
                        {{ contentFieldsSpec.label }}
                    </div>
                    <div class="text-gray-600">
                        {{ contentFieldsSpec.description }}
                    </div>
                    <a
                        class="flex button mt-2"
                        @click="selectContentFieldType(contentFieldsSpec.type)"
                    >
                        {{ $t("addField") }}
                    </a>
                </div>
            </div>
        </div>
    </OffPanel>

    <OffPanel
        name="fieldSchemaForm"
        width="65%"
    >
        <div slot="offPanelTitle">{{ contentFieldSpecInForm.label }}</div>
        <div slot="offPanelBody">
            <FieldSchemaForm
                ref="FieldSchemaForm"
                :contentFieldSpec="contentFieldSpecInForm"
                :fieldSchema="fieldSchemaInForm"
            />

            <button
                class="button is-blue w-full"
                @click="saveFieldSchemaInForm()"
            >
                {{ $t("validate") }}
            </button>
        </div>
    </OffPanel>
</div>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import Vue from "vue"
import { createItemValidation, createItemWarnings } from "@js/items/itemsUtils"
import PilotMixin from "@components/PilotMixin"

import FullLayout from "@components/layout/FullLayout"
import AdminButton from "@components/admin/AdminButton"

import ItemTypeFormSchemaMixin from "./ItemTypeFormSchemaMixin.vue"
import ItemContentFormField from "@views/items/contentForm/ItemContentFormField.vue"
import FieldSchemaForm from "./FieldSchemaForm.vue"
import ItemContentFieldIcon from "./ItemContentFieldIcon.vue"

import { SlickList, SlickItem } from "vue-slicksort"

export default {
    name: "ItemTypeEdit",
    mixins: [PilotMixin, ItemTypeFormSchemaMixin],
    components: {
        FullLayout,
        AdminButton,
        ItemContentFormField,
        FieldSchemaForm,
        ItemContentFieldIcon,

        SlickList,
        SlickItem,
    },
    data: () => ({
        // v-model of the field schema
        fieldSchemaInForm: {},
        // Fake v-model and validation to simulate actual usage of the displayed fields with an item
        fakeItemContentModel: {
            content: {},
        },
        fakeItemValidation: {},
        fakeItemWarnings: {},
        // Index in the field schema list
        // In creation, the new field schema will be inserted after this index
        // In edition, this is the index of the existing field schema
        fieldSchemaIndex: null,
        // distinguish between add and edition
        isFieldSchemaEdition: false,
        // field schema requested for deletion. Wait for confirmation
        fieldSchemaDeletionRequested: false,
        fieldPreview: false,
    }),
    computed: {
        ...mapState("itemTypes", ["contentFieldSpecs"]),
        ...mapState("loading", ["loadingInProgress", "loadingStatus"]),
        ...mapGetters("itemTypes", ["itemTypeId", "itemType"]),
        ...mapGetters("loading", ["getErrorMessage"]),
        ...mapGetters("users", ["myPermissions"]),
        contentFieldSpecsDict() {
            return _.keyBy(this.contentFieldSpecs, (spec) => spec.type)
        },
        contentFieldSpecInForm() {
            return this.contentFieldSpecsDict[this.fieldSchemaInForm.type] || {}
        },
    },
    methods: {
        ...mapMutations("itemTypes", ["partialUpdateItemTypeInList"]),
        ...mapMutations("loading", ["resetLoading"]),
        ...mapActions("itemTypes", ["partialUpdateItemType"]),
        setupValidation() {
            if (!this.itemType.content_schema) {
                return
            }

            this.fakeItemValidation = createItemValidation(
                this.itemType.content_schema,
                this.itemType.metadata_schema,
                this.fakeItemContentModel,
            )
            this.fakeItemWarnings = createItemWarnings(
                this.itemType.content_schema,
                this.fakeItemContentModel,
            )
        },

        onFormSaved(itemType) {
            this.partialUpdateItemTypeInList(itemType)
        },
        updateContentSchema(contentSchema) {
            this.partialUpdateItemType({
                id: this.itemTypeId,
                content_schema: contentSchema,
            })
                .then((response) => {
                    setTimeout(() => this.resetLoading("partialUpdateItemType"), 1500)
                })
                .catch((error) => {
                    setTimeout(() => this.resetLoading("partialUpdateItemType"), 5000)
                })
        },
        onContentSchemaSorted(newContentSchema) {
            this.updateContentSchema(newContentSchema)
        },
        startFieldSchemaAdd() {
            this.fieldSchemaInForm = {}
            this.isFieldSchemaEdition = false
            this.openOffPanel("selectFieldSchemaType")
        },
        selectContentFieldType(contentFieldType) {
            this.fieldSchemaInForm = {
                type: contentFieldType,
            }
            this.openOffPanel("fieldSchemaForm")
            this.closeOffPanel("selectFieldSchemaType")
        },
        startFieldSchemaEdition(fieldSchema, fieldSchemaIndex) {
            this.fieldSchemaInForm = _.cloneDeep(fieldSchema)
            this.fieldSchemaIndex = fieldSchemaIndex
            this.isFieldSchemaEdition = true
            this.openOffPanel("fieldSchemaForm")
        },
        saveFieldSchemaInForm() {
            let vuelidate = this.$refs.FieldSchemaForm.$v
            vuelidate.$touch()
            if (vuelidate.$invalid) {
                return
            }

            let newContentSchema = _.cloneDeep(this.itemType.content_schema)
            if (this.isFieldSchemaEdition) {
                newContentSchema.splice(this.fieldSchemaIndex, 1, this.fieldSchemaInForm)
            } else {
                newContentSchema.splice(1, 0, this.fieldSchemaInForm)
            }

            this.updateContentSchema(newContentSchema)
            this.fieldSchemaInForm = {}
            this.closeOffPanel("fieldSchemaForm")
        },
        getFieldHumanName(fieldSchema) {
            if (!this.contentFieldSpecsDict[fieldSchema.type]) {
                return "?"
            }
            return this.contentFieldSpecsDict[fieldSchema.type].label
        },
        toggleFieldPreview(fieldname) {
            this.fieldPreview = !this.fieldPreview
        },
        requestFieldSchemaDeletion(fieldSchema) {
            this.fieldSchemaDeletionRequested = fieldSchema
        },
        confirmFieldSchemaDeletion() {
            let newContentSchema = this.itemType.content_schema.filter(
                (schema) => schema.name != this.fieldSchemaDeletionRequested.name,
            )
            this.updateContentSchema(newContentSchema)
        },
        cancelFieldSchemaDeletion() {
            this.fieldSchemaDeletionRequested = null
        },
        updateItemFormFieldValue({ fieldName, value }) {
            Vue.set(this.fakeItemContentModel.content, fieldName, value)
        },
    },
    watch: {
        itemType: {
            deep: true,
            immediate: true,
            handler() {
                this.setupValidation()
            },
        },
    },
    beforeDestroy() {
        this.fakeItemValidation.freeMemory()
        this.fakeItemWarnings.freeMemory()
    },
    i18n: {
        messages: {
            fr: {
                add: "Ajouter un champ",
                addField: "Ajouter",
                addFieldSchema: "Ajouter un champ",
                confirmDeletion: "Ok, supprimer le champ ET ses données",
                deleteField: "Supprimer le champ",
                dragToOrder: "Glissez-déplacez pour ré-ordonner",
                dragHelpText: "Déplacer pour réordonner",
                editOtherFields: "Modifier les paramètres",
                fieldDeletionWarning:
                    "Attention la suppression d'un champ entraine la suppression des données qui y sont stockées",
                fieldSchemaForm: "Champ de formulaire",
                fieldSchemaType: "Type de champ",
                linkedItemsCount:
                    "{linkedItemsCount} contenu associé | {linkedItemsCount} contenus associés",
                previewFields: "Aperçu des champs",
                saveItemInProgress: "Sauvegarde en cours...",
                saveItemTypeOk: "Type de contenu sauvegardé",
                saveItemTypeError: "Erreur lors de la sauvegarde du type de contenu",
                selectFieldSchemaType: "Choisissez le type de champ à ajouter",
            },
            en: {
                add: "Add a field",
                addField: "Add this field",
                addFieldSchema: "Add a field",
                confirmDeletion: "Ok, delete the field AND its data",
                deleteField: "Delete the field",
                dragToOrder: "Drag and drop to re-order",
                dragHelpText: "Move to re-order",
                editOtherFields: "Edit other fields",
                fieldDeletionWarning:
                    "Warning, deleting a field will also delete the associated data",
                fieldSchemaForm: "Form field",
                fieldSchemaType: "Field type",
                linkedItemsCount:
                    "{linkedItemsCount} associated content | {linkedItemsCount} associated contents",
                previewFields: "Preview all fields",
                saveItemInProgress: "Save in progress...",
                saveItemTypeOk: "Content type saved",
                saveItemTypeError: "Error while saving the item type",
                selectFieldSchemaType: "Select the field type to add",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.ItemSaveLoadingBackdrop {
    background-color: rgba(12, 12, 12, 0.33);
    display: block;
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    top: 0;
    z-index: 20;
}
.ItemSaveLoadingMessage {
    @apply bg-white rounded mx-auto;
    display: block;
    z-index: 21;
    position: fixed;
    left: 50%;
    text-align: center;
    padding: 15px;
    width: 400px;
    margin-left: -165px; // = (messageWidth - leftMenuWidth) / 2 = (400 - 70) / 2 = 165
}

.ItemTypeEditApp__dragHandle {
    margin-right: 1em;
    cursor: grab;
}

.ItemTypeEditApp__DragHelpText {
    display: none;
}
.ItemTypeEditApp__SortableHelper {
    z-index: 20;

    .ItemTypeEditApp__DragHelpText {
        display: inline;
    }
}
</style>
