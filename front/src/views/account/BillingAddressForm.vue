<template>
<div class="BillingAddressForm">
    <FormField
        :schema="{
            type: 'char',
            label: $t('billingName'),
            placeholder: $t('billingName'),
        }"
        v-model.trim="organization.billing_name"
        :vuelidate="$v.organization.billing_name"
    />

    <FormField
        :schema="{
            type: 'text',
            label: $t('billingAddress'),
            placeholder: $t('billingAddress'),
        }"
        v-model.trim="organization.billing_address"
        :vuelidate="$v.organization.billing_address"
    />

    <div class="flex flex-row">
        <FormField
            class="w-32 mr-4"
            :schema="{
                type: 'char',
                label: $t('billingPostalCode'),
                placeholder: $t('billingPostalCode'),
            }"
            v-model.trim="organization.billing_postal_code"
        />

        <FormField
            class="w-32 flex-grow mr-4"
            :schema="{
                type: 'char',
                label: $t('billingCity'),
                placeholder: $t('billingCity'),
            }"
            v-model.trim="organization.billing_city"
        />

        <FormField
            class="w-32 flex-grow"
            :schema="{
                type: 'char',
                label: $t('billingVAT'),
                placeholder: $t('billingVAT'),
            }"
            v-model.trim="organization.billing_vat"
        />
    </div>
</div>
</template>

<script>
import { required } from "vuelidate/lib/validators"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "BillingAddressForm",
    mixins: [PilotMixin],
    props: {
        organization: Object,
    },
    validations: {
        organization: {
            billing_name: { required },
            billing_address: { required },
        },
    },
    i18n: {
        messages: {
            fr: {
                billingName: "Nom",
                billingAddress: "Rue",
                billingPostalCode: "Code postal",
                billingCity: "Ville",
                billingVAT: "Numéro de TVA",
            },
            en: {
                billingName: "Name",
                billingAddress: "Street",
                billingPostalCode: "Postal Code",
                billingCity: "City",
                billingVAT: "VAT Number",
            },
        },
    },
}
</script>
