<template>
<div class="FieldSchemaForm">
    <!-- ================= -->
    <!-- Common attributes -->
    <!-- ================= -->

    <FormField
        v-model="fieldSchema.label"
        :schema="{
            type: 'char',
            label: this.$t('label'),
        }"
        :vuelidate="$v.fieldSchema.label"
    />

    <FormField
        v-model="fieldSchema.help_text"
        :schema="{
            type: 'text',
            label: this.$t('helpText'),
            help_text: $t('allowedHtmlTags') + ' : <ul> <ol> <li> <strong> <em>',
        }"
    />

    <FormField
        v-if="contentFieldSpec.can_be_required"
        v-model="fieldSchema.required"
        :schema="{
            type: 'toggle',
            label: this.$t('required'),
        }"
    />

    <FormField
        v-if="contentFieldSpec.can_be_elastic"
        v-model="fieldSchema.elastic"
        :schema="{
            type: 'toggle',
            label: this.$t('elastic'),
            help_text: $t('elasticExplain'),
        }"
    />

    <FormField
        v-model="fieldSchema.show_in_creation"
        :schema="{
            type: 'toggle',
            label: this.$t('showInCreation'),
            help_text: $t('showInCreationExplain'),
        }"
    />

    <FormField
        v-model="fieldSchema.show_in_public"
        :schema="{
            type: 'toggle',
            label: this.$t('showInPublic'),
            help_text: $t('showInPublicExplain'),
        }"
    />

    <!-- Which type to use ? -->

    <div
        v-if="contentFieldSpec.with_initial"
        class="form__field"
    >
        <label>
            <div class="form__field__label">{{ $t("initialValue") }}</div>
            <input
                v-if="fieldSchema.type == 'char'"
                v-model="fieldSchema.initial"
                type="text"
            />
            <textarea
                v-if="fieldSchema.type == 'text'"
                v-model="fieldSchema.initial"
            />
        </label>
    </div>

    <!-- ======================== -->
    <!-- Type-specific attributes -->
    <!-- ======================== -->

    <!-- For Textual types -->

    <FormField
        v-if="contentFieldSpec.with_placeholder"
        v-model="fieldSchema.placeholder"
        :schema="{
            type: 'char',
            label: this.$t('placeholder'),
        }"
    />

    <FormField
        v-if="contentFieldSpec.with_max_length"
        v-model="fieldSchema.max_length"
        :schema="{
            type: 'char',
            label: this.$t('maxLength'),
        }"
        :vuelidate="$v.fieldSchema.max_length"
    />

    <FormField
        v-if="contentFieldSpec.with_validate_max_length"
        v-model="fieldSchema.validate_max_length"
        :schema="{
            type: 'toggle',
            label: this.$t('validateMaxLength'),
            help_text: $t('validateMaxLength_explain'),
        }"
    />

    <!-- For Number types -->

    <FormField
        v-if="contentFieldSpec.with_min_value"
        v-model="fieldSchema.min_value"
        :schema="{
            type: 'char',
            label: this.$t('minValue'),
        }"
        :vuelidate="$v.fieldSchema.min_value"
    />

    <FormField
        v-if="contentFieldSpec.with_max_value"
        v-model="fieldSchema.maxValue"
        :schema="{
            type: 'char',
            label: this.$t('maxValue'),
        }"
        :vuelidate="$v.fieldSchema.maxValue"
    />

    <!-- For Choice types -->

    <div
        v-if="contentFieldSpec.with_choices"
        class="form__field flex flex-col justify-center"
    >
        <div class="form__field__label mb-2">{{ $t("choices") }}</div>
        <div
            v-for="(choice, index) in fieldSchema.choices"
            class="flex mb-2"
            :key="index"
        >
            <span class="flex flex-shrink-0 items-center mr-1 text-sm text-gray-600">
                {{ $t("choice") }} {{ index + 1 }} :
            </span>
            <input
                v-model="choice[1]"
                type="text"
            />
            <button
                class="button ml-1"
                @click="removeChoice(index)"
            >
                <Icon name="Close" />
            </button>
        </div>
        <button
            class="mb-1 button mx-auto w-full"
            @click="addChoice()"
        >
            {{ $t("add") }}
        </button>
    </div>

    <!-- Advanced attributes -->

    <div>
        <a
            v-if="contentFieldSpec.with_regex && !isAdvancedAttributesVisible"
            class="button flex my-4 justify-center"
            @click="isAdvancedAttributesVisible = true"
        >
            {{ $t("advancedParameters") }}
        </a>
        <a
            v-if="contentFieldSpec.with_regex && isAdvancedAttributesVisible"
            class="button flex my-4 justify-center"
            @click="isAdvancedAttributesVisible = false"
        >
            {{ $t("hide") }}
        </a>

        <div v-if="isAdvancedAttributesVisible">
            <FormField
                v-if="contentFieldSpec.with_regex"
                v-model="fieldSchema.regex"
                :schema="{
                    type: 'char',
                    label: this.$t('regex'),
                }"
            />

            <FormField
                v-if="contentFieldSpec.with_regex"
                v-model="fieldSchema.regex_error_message"
                :schema="{
                    type: 'char',
                    label: this.$t('regexErrorMessage'),
                }"
            />
        </div>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import Vue from "vue"
import { required, numeric } from "vuelidate/lib/validators"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "FieldSchemaForm",
    mixins: [PilotMixin],
    props: {
        fieldSchema: {
            type: Object,
            required: true,
        },
        contentFieldSpec: {
            type: Object,
            required: true,
        },
    },
    data: () => ({
        isAdvancedAttributesVisible: false,
    }),
    validations: {
        fieldSchema: {
            label: { required },
            max_length: { numeric },
            min_value: { numeric },
            max_value: { numeric },
        },
    },
    methods: {
        addChoice() {
            let newKey = _.max(this.fieldSchema.choices.map((choice) => choice[0])) + 1
            this.fieldSchema.choices.push([newKey, ""])
        },
        removeChoice(index) {
            this.fieldSchema.choices.splice(index, 1)
        },
    },
    created() {
        if (this.contentFieldSpec.with_choices && !this.fieldSchema.choices) {
            Vue.set(this.fieldSchema, "choices", [[0, ""]])
        }
    },
    i18n: {
        messages: {
            fr: {
                advancedParameters: "Paramètres avancés",
                allowedHtmlTags: "Balises HTML autorisées",
                choice: "Choix",
                choices: "Choix disponibles",
                elastic: "Peut être répété",
                elasticExplain:
                    "Un ± apparaitra sous le champ et permettra au rédacteur de multiplier ce champ dans le formulaire",
                hideFieldSchemaForm__advancedParameters: "Masquer les paramètres avancés",
                initialValue: "Valeure initiale (utilisée à la création du contenu)",
                label: "Nom du champ",
                maxLength: "Nombre de caractères maximum",
                maxValue: "Valeur max.",
                minValue: "Valeur min.",
                placeholder: "Exemple de saisie (apparait en grisé à l'intérieur du champ vide)",
                regex: "Regex",
                regexErrorMessage: "Message d'erreur regex",
                required: "Ce champ devra obligatoirement être saisi",
                showInCreation: "Ce champ apparait dans le formulaire de création du contenu",
                showInCreationExplain:
                    "Pour saisir rapidement des informations essentielles au contenu",
                showInPublic: "Ce champ apparait dans les formulaires publics",
                showInPublicExplain:
                    "Lorsque le formulaire de ce contenu est partagé publiquement ce champ apparait",
                validateMaxLength: "Le nombre maximum de caractères ne doit pas être dépassé",
                validateMaxLength_explain:
                    "Si activé, l'utilisateur verra une erreur de validation quand ce champ compte plus de caractères que la limite autorisée. Si désactivé, l'utilisateur peut dépasser la limite (on l'avertit cependant)",
            },
            en: {
                advancedParameters: "Advanced parameters",
                allowedHtmlTags: "Allowed html tags",
                choice: "Choice",
                choices: "Choices available",
                elastic: "Can be repeated",
                elasticExplain:
                    "A ± will appear under the field and allow the writer to multiply this field in the form",
                hideFieldSchemaForm__advancedParameters: "Hide advanced parameters",
                initialValue: "Initial value (set at content creation)",
                label: "Field label",
                maxLength: "Maximum number of characters",
                maxValue: "Max. value",
                minValue: "Min. Value",
                placeholder: "Example of entry (appears in grey inside the empty field)",
                regex: "Regex",
                regexErrorMessage: "Regex error message",
                required: "This field must be filled in",
                showInCreation: "This field appears in the content creation form",
                showInCreationExplain: "To quickly enter information essential to the content",
                showInPublic: "This field appears in public forms",
                showInPublicExplain:
                    "When the form for this content is shared publicly this field appears",
                validateMaxLength: "The maximum number of characters must not be exceeded",
                validateMaxLength_explain:
                    "If active, then the user will see a validation error if this field has more characters than the allowed limit. If inactive, the user can exceed the limit (he is warned however)",
            },
        },
    },
}
</script>
