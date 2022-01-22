<template>
<BaseForm
    :model="assetRightModel"
    :saveUrl="urls.assetRights"
    :vuelidate="$v.assetRightModel"
    @cancel="closeOffPanel('assetRightForm')"
    @saved="$emit('saved', $event)"
>
    <FormField
        v-model="assetRightModel.expiry"
        :schema="{
            type: 'date',
            label: $t('expiry'),
            formatWithoutTime: true,
        }"
        :vuelidate="$v.assetRightModel.expiry"
    />

    <div class="form__field">
        <div class="form__field__label">{{ $t("assetMedium") }}</div>
        <Label
            v-if="assetRightModel.medium"
            :goToListOnClick="false"
            :label="assetRightModel.medium"
        />
        <br />

        <LabelSelect
            :multiple="false"
            placement="right"
            :sortable="true"
            targetType="asset_right_medium"
            triggerElementName="PopperRef"
            :value="assetRightModel.medium"
            @input="onMediumInput"
        >
            <template #triggerElement>
                <a ref="PopperRef">{{ $t("selectMedium") }}</a>
            </template>
        </LabelSelect>

        <ValidationErrors :validation="$v.assetRightModel.medium_id" />
    </div>
</BaseForm>
</template>

<script>
import _ from "lodash"
import Vue from "vue"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { required } from "vuelidate/lib/validators"
import PilotMixin from "@components/PilotMixin"

import LabelSelect from "@views/labels/LabelSelect.vue"
import Label from "@views/labels/Label.vue"

export default {
    name: "AssetRightForm",
    mixins: [PilotMixin],
    components: {
        LabelSelect,
        Label,
    },
    props: {
        assetRight: Object,
        assetId: Number,
    },
    data: () => ({
        assetRightModel: {
            asset_id: null,
            expiry: null,
            id: null,
            medium: null,
            medium_id: null,
        },
        medium: {},
    }),
    validations: {
        assetRightModel: {
            expiry: { required },
            medium_id: { required },
        },
    },
    methods: {
        ...mapMutations("offPanel", ["closeOffPanel"]),
        onMediumInput(medium) {
            Vue.set(this.assetRightModel, "medium", medium)
            this.assetRightModel.medium_id = medium.id
            this.$v.assetRightModel.medium_id.$touch()
        },
    },
    created() {
        this.assetRightModel = _.pick(this.assetRight, ["id", "expiry", "medium", "medium_id"])
        this.assetRightModel.asset_id = this.assetId
    },
    i18n: {
        messages: {
            fr: {
                selectMedium: "Sélectionner le support d'utilisation",
            },
            en: {
                selectMedium: "Select usage medium",
            },
        },
    },
}
</script>
