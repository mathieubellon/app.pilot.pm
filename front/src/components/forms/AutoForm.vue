<template>
<BaseForm
    :callToActionText="callToActionText"
    :disableSave="disableSave"
    :errorText="errorText"
    :model="model"
    :saveUrl="saveUrl"
    :showCancel="showCancel"
    :successText="successText"
    :urlParams="urlParams"
    :vuelidate="$v.model"
    @cancel="$emit('cancel')"
    @saved="$emit('saved', $event)"
>
    <FormField
        v-for="fieldSchema in schema"
        v-model="model[fieldSchema.name]"
        :key="fieldSchema.name"
        :schema="fieldSchema"
        :vuelidate="$v.model[fieldSchema.name]"
    />
</BaseForm>
</template>

<script>
import _ from "lodash"
import Vue from "vue"
import { createFieldValidation } from "@js/validation.js"

import BaseForm from "@components/forms/BaseForm.vue"
import FormField from "@components/forms/FormField.vue"

export default {
    name: "AutoForm",
    components: {
        BaseForm,
        FormField,
    },
    props: {
        schema: Array,
        saveUrl: { required: true },
        urlParams: {
            type: Object,
            required: false,
            default: () => {},
        },
        initialData: Object,
        callToActionText: String,
        successText: String,
        errorText: String,
        showCancel: {
            type: Boolean,
            default: true,
        },
        disableIfUnchanged: Boolean,
    },
    data: () => ({
        model: {},
    }),
    watch: {
        initialData() {
            this.initModel()
        },
    },
    computed: {
        disableSave() {
            return this.disableIfUnchanged && _.isEqual(this.model, this.initialData)
        },
    },
    methods: {
        initModel() {
            for (let fieldSchema of this.schema) {
                if (
                    fieldSchema.type == "char" ||
                    fieldSchema.type == "password" ||
                    fieldSchema.type == "text"
                ) {
                    Vue.set(this.model, fieldSchema.name, "")
                }
            }
            for (let fieldName in this.initialData) {
                Vue.set(this.model, fieldName, this.initialData[fieldName])
            }
        },
    },
    validations() {
        let v = { model: {} }
        for (let fieldSchema of this.schema) {
            v.model[fieldSchema.name] = createFieldValidation(fieldSchema)
        }
        return v
    },
    created() {
        this.initModel()
    },
}
</script>
