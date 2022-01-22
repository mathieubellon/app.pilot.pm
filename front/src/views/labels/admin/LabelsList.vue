<template>
<div>
    <div class="mb-5">
        <router-link :to="{ name: 'labels' }">{{ $t("labels") }} /</router-link>

        <span class="text-gray-700">
            {{ targetTypeDisplay }}
        </span>
    </div>

    <VueFuse
        class="mb-5"
        :defaultAll="true"
        :keys="['name']"
        :list="labels"
        :placeholder="$t('search')"
        :shouldSort="false"
        :threshold="0.1"
        @result="onFuseResult"
    />

    <Loadarium name="fetchLabels">
        <LabelsListBulkbar />

        <AdminList
            :checkPerm="false"
            :instancesList="filteredLabels"
            :sortable="targetTypeSpec.sortable"
            @delete="deleteLabel"
            @edit="startLabelEdition"
            @sorted="onLabelsSorted"
        >
            <template slot-scope="{ instance }">
                <div
                    v-if="myPermissions.is_admin"
                    class="mr-4"
                >
                    <input
                        :checked="isSelectedForBulkAction(instance)"
                        type="checkbox"
                        @change="toggleForBulkAction(instance)"
                    />
                </div>
                <Label
                    :goToListOnClick="true"
                    :label="instance"
                />
            </template>
        </AdminList>

        <div
            v-if="labels.length === 0"
            class="help-text"
        >
            <div class="help-text-title">
                <Icon
                    class="help-text-icon"
                    name="Tag"
                />
                <span>{{ $t("listEmpty") }}</span>
            </div>
            <button
                class="button is-blue"
                @click="startLabelCreation()"
            >
                {{ $t("add") }}
            </button>
        </div>
    </Loadarium>

    <OffPanel
        name="labelForm"
        @opened="onOpenLabelFormPanel"
    >
        <div slot="offPanelTitle">{{ $t("add") }}</div>
        <div slot="offPanelBody">
            <BaseForm
                :model="labelInForm"
                :saveUrl="urls.labels"
                :vuelidate="vuelidate"
                @cancel="closeOffPanel('labelForm')"
                @saved="onLabelSaved"
            >
                <LabelForm
                    ref="labelForm"
                    :labelModel="labelInForm"
                />
            </BaseForm>
        </div>
    </OffPanel>
</div>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { sortByAlphaString } from "@js/utils.js"
import PilotMixin from "@components/PilotMixin"

import AdminButton from "@components/admin/AdminButton"
import AdminList from "@components/admin/AdminList.vue"

import Label from "../Label.vue"
import LabelForm from "./LabelForm.vue"
import LabelsListBulkbar from "./LabelsListBulkbar.vue"
import { DEFAULT_LABEL_BG_COLOR, DEFAULT_LABEL_COLOR } from "@/store/modules/LabelStore"

const EMPTY_LABEL = {
    name: "",
    color: DEFAULT_LABEL_COLOR,
    background_color: DEFAULT_LABEL_BG_COLOR,
}

export default {
    name: "LabelsList",
    mixins: [PilotMixin],
    components: {
        AdminButton,
        AdminList,

        Label,
        LabelForm,
        LabelsListBulkbar,
    },
    data: () => ({
        filteredLabels: [],
        // The channel type currently displayed in the form. May be a creation or an edition
        labelInForm: _.clone(EMPTY_LABEL),
        vuelidate: null,
    }),
    computed: {
        ...mapState("bulk", ["bulkActionSelection"]),
        ...mapGetters("users", ["myPermissions"]),
        labels() {
            let labels = this.$store.state.labels.labels[this.targetType] || []
            // If the drag'n'drop is disabled, the order is not defined by the user,
            // but we sort the labels alphabetically
            if (!this.targetTypeSpec.sortable) {
                labels = sortByAlphaString(labels, (label) => label.name)
            }
            return labels
        },
        targetType() {
            return this.$route.params.targetType
        },
        targetTypeSpec() {
            return _.find(
                this.$store.state.labels.targetTypeSpecs,
                (tts) => tts.name == this.targetType,
            )
        },
        targetTypeDisplay() {
            return this.targetTypeSpec.model + " / " + this.targetTypeSpec.fieldNamePlural
        },
    },
    methods: {
        ...mapMutations("labels", ["setLabels", "updateLabel", "appendToLabels"]),
        ...mapActions("labels", ["fetchLabels", "setLabelsOrder", "deleteLabel"]),
        ...mapMutations("bulk", ["toggleForBulkAction"]),
        onOpenLabelFormPanel() {
            setTimeout(() => {
                this.vuelidate = this.$refs.labelForm.$v
            })
        },
        startLabelCreation() {
            this.labelInForm = _.assign({}, EMPTY_LABEL, {
                target_type: this.targetType,
                order: this.labels.length,
            })
            this.openOffPanel("labelForm")
        },
        startLabelEdition(label) {
            this.labelInForm = _.assign({}, label)
            this.openOffPanel("labelForm")
        },
        isSelectedForBulkAction(label) {
            return this.bulkActionSelection[label.id]
        },
        onLabelSaved(label) {
            // Edition
            if (this.labelInForm.id) {
                this.updateLabel(label)
            }
            // Creation
            else {
                this.appendToLabels(label)
            }
            this.closeOffPanel("labelForm")
        },
        onLabelsSorted(newLabels) {
            // On sorting, we get only the visible labels
            // If there's a fuse filtering, we'll need to add back the invisible labels (filtered out by fuse)
            if (newLabels.length < this.labels.length) {
                newLabels = newLabels.concat(_.differenceBy(this.labels, newLabels, "id"))
            }

            let newLabelsOrder = newLabels.map((label, index) => ({ id: label.id, order: index }))

            // Consider the new ordering will be accepted by the backend.
            // This is to prevent the element to flicker when waiting the response from the backend
            this.setLabels({ targetType: this.targetType, labels: newLabels })

            // Ask the backend to actually save the new order
            // It will respond with the current state of the label order, which should be the same than ours.
            this.setLabelsOrder({
                targetType: this.targetType,
                labelOrder: newLabelsOrder,
            })
        },
        onFuseResult(filteredLabels) {
            this.filteredLabels = filteredLabels
        },
    },
    created() {
        this.fetchLabels(this.targetType)
    },
    i18n: {
        messages: {
            fr: {
                back: "Retour",
                listEmpty: "Cette liste est vide pour le moment",
            },
            en: {
                back: "Back",
                listEmpty: "This list is empty at the moment",
            },
        },
    },
}
</script>
