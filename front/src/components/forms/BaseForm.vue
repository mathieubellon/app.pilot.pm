<template>
<form
    class="BaseForm"
    :class="{ stretched }"
    @submit.prevent="submit"
>
    <div class="BaseForm__fields">
        <slot />
    </div>

    <div class="BaseForm__bottom">
        <slot name="bottom" />

        <div
            v-if="axiosError"
            class="form__field__error mt-4"
        >
            <span v-html="getAxiosErrorMessage(axiosError)" />
        </div>

        <div class="BaseForm__buttons">
            <!--
            Here we need to define type="submit" on the validation button,
            so it's the default action when hitting "enter".
            For exammple, this will avoid triggering the showFields/hideFields on AddForms.
            -->
            <ButtonSpinner
                class="is-blue w-full"
                :disabled="isButtonDisabled"
                :errorText="errorText"
                :isLoading="showLoading"
                :status="status"
                :successText="successText"
                type="submit"
            >
                <span>{{ callToActionText ? callToActionText : $t("save") }}</span>
            </ButtonSpinner>

            <button
                v-if="showCancel"
                class="button is-white mt-2 w-full"
                :disabled="showLoading"
                type="button"
                @click.prevent="cancel"
            >
                <span>{{ $t("cancel") }}</span>
            </button>
        </div>
    </div>
</form>
</template>

<script>
import _ from "lodash"
import { $http } from "@js/ajax"
import { getAxiosErrorMessage } from "@js/errors"

import ButtonSpinner from "@components/ButtonSpinner"

export default {
    name: "BaseForm",
    components: {
        ButtonSpinner,
    },
    props: {
        model: {
            type: Object,
            required: true,
        },
        vuelidate: Object,
        saveUrl: Object,
        urlParams: {
            type: Object,
            required: false,
            default: () => {},
        },
        extraData: {
            type: Object,
            required: false,
            default: () => {},
        },
        callToActionText: String,
        successText: String,
        errorText: String,
        resetTimeout: {
            type: Number,
            default: 2000,
        },
        showCancel: {
            type: Boolean,
            default: true,
        },
        disableSave: {
            type: Boolean,
            default: false,
        },
        partialSave: Boolean,
        stretched: {
            type: Boolean,
            default: false,
        },
    },
    data: () => ({
        showLoading: false,
        status: "",
        axiosError: null,
        getAxiosErrorMessage,
    }),
    methods: {
        submit() {
            if (this.isButtonDisabled || this.status == "success") return

            if (this.vuelidate) {
                this.vuelidate.$touch()

                if (this.vuelidate.$invalid) {
                    return
                }
            }

            if (this.saveUrl) {
                this.showLoading = true
                this.axiosError = null

                let urlParams = this.urlParams ? _.cloneDeep(this.urlParams) : {},
                    method

                let data = _.cloneDeep(this.model)
                if (this.extraData) {
                    _.assign(data, this.extraData)
                }

                // If we have an id, we are in an update context
                if (this.model.id) {
                    urlParams.id = this.model.id
                    method = this.partialSave ? "patch" : "put"
                }
                // Else it's a create context
                else {
                    method = "post"
                }

                this.reset()
                $http({
                    method: method,
                    url: this.saveUrl.format(urlParams),
                    data: data,
                })
                    .then((response) => {
                        this.showLoading = false
                        this.status = "success"

                        setTimeout(() => {
                            this.status = ""
                            this.reset()
                        }, this.resetTimeout)

                        this.$emit("saved", response.data)
                    })
                    .catch((error) => {
                        this.showLoading = false
                        this.status = "error"
                        this.axiosError = error

                        // Move the server side errors into the vuelidate object,
                        // so they can be rendered by <ValidationErrors> component
                        if (this.vuelidate && error.response) {
                            let errorDict = error.response.data
                            for (let fieldName in errorDict) {
                                if (this.vuelidate[fieldName]) {
                                    this.vuelidate[fieldName].serverSide = errorDict[fieldName]
                                    delete errorDict[fieldName]
                                }
                            }
                            // This line is ABSOLUTELY VITAL. It force the validation errors re-rendering in <ValidationErrors>.
                            // this.$forceUpdate() won't work, because Vue reactivity doesn't know about our serverSide property
                            this.vuelidate.$model = _.clone(this.vuelidate.$model)
                        }

                        setTimeout(() => {
                            this.status = ""
                        }, 4000)

                        this.$emit("error", error)
                    })
            }

            this.$emit("submit")
        },
        reset() {
            // Reset the validation if provided
            if (this.vuelidate) {
                this.vuelidate.$reset()
                for (let fieldName in this.vuelidate) {
                    if (this.vuelidate[fieldName] && this.vuelidate[fieldName].serverSide) {
                        delete this.vuelidate[fieldName].serverSide
                    }
                }
            }
        },
        cancel() {
            this.reset()
            this.$emit("cancel")
        },
    },
    computed: {
        isButtonDisabled() {
            return (this.vuelidate && this.vuelidate.$error) || this.showLoading || this.disableSave
        },
    },
    mounted() {
        this.$el.addEventListener("CharInputWrappingSubmit", this.submit)
    },
}
</script>

<style>
.BaseForm.stretched {
    @apply flex flex-col flex-auto h-0;

    .BaseForm__fields {
        @apply flex-auto overflow-y-auto mb-0 p-4 pt-0;
    }

    .BaseForm__bottom {
        @apply flex-shrink-0 border-t border-gray-400 bg-white p-4;
    }
}

.BaseForm__fields {
    @apply mb-8;
}
</style>
