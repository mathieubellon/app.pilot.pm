<template>
<transition
    v-if="anySelectedForBulkAction"
    enter-active-class="animated animated-500 fadeIn"
    leave-active-class="animated animated-500 fadeOut"
>
    <div class="LabelsListBulkbar">
        <BulkBar :instances="labels">
            <div class="flex">
                <template v-if="!deletionRequested">
                    <button
                        class="button is-yellow mr-4"
                        @click="openOffPanel('labelsMerge')"
                    >
                        {{ $t("action.merge") }}
                    </button>

                    <button
                        class="button is-red"
                        @click="deletionRequested = true"
                    >
                        {{ $t("action.delete") }}
                    </button>
                </template>

                <div
                    v-else
                    class="flex py-2 px-4 bg-white rounded items-center border border-black"
                >
                    <span>{{ $tc("areYouSureDeletion", bulkActionSelectionAsList.length) }}</span>
                    <SmartButtonSpinner
                        class="ml-2 mr-4 is-red"
                        name="bulkAction-delete"
                        :timeout="1500"
                        @click="bulkDelete"
                    >
                        {{ $t("confirmDeletion") }}
                    </SmartButtonSpinner>
                    <button
                        class="button is-outlined"
                        @click="cancelDeletion"
                    >
                        {{ $t("cancel") }}
                    </button>
                </div>
            </div>
        </BulkBar>

        <OffPanel
            name="labelsMerge"
            @opened="onOpenMergePanel"
        >
            <div slot="offPanelTitle">{{ $t("merge") }}</div>
            <div slot="offPanelBody">
                <LabelForm
                    ref="labelForm"
                    :labelModel="labelMergeDestination"
                />

                <SmartButtonSpinner
                    name="mergeLabels"
                    :disabled="vuelidate && vuelidate.$invalid"
                    @click="mergeLabels"
                >
                    {{ $t("merge") }}
                </SmartButtonSpinner>
            </div>
        </OffPanel>
    </div>
</transition>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls"
import PilotMixin from "@components/PilotMixin"

import BulkBar from "@components/BulkBar.vue"
import LabelForm from "./LabelForm.vue"
import { DEFAULT_LABEL_BG_COLOR, DEFAULT_LABEL_COLOR } from "@/store/modules/LabelStore"

const EMPTY_LABEL = {
    name: "",
    color: DEFAULT_LABEL_COLOR,
    background_color: DEFAULT_LABEL_BG_COLOR,
}

export default {
    name: "LabelsListBulkbar",
    mixins: [PilotMixin],
    components: {
        BulkBar,
        LabelForm,
    },
    data: () => ({
        labelMergeDestination: _.clone(EMPTY_LABEL),
        vuelidate: null,
        deletionRequested: false,
    }),
    computed: {
        ...mapGetters("choices", [
            "channelChoices",
            "projectChoices",
            "targetChoices",
            "usersChoices",
        ]),
        ...mapGetters("bulk", ["anySelectedForBulkAction", "bulkActionSelectionAsList"]),
        targetType() {
            return this.$route.params.targetType
        },
        labels() {
            return this.$store.state.labels.labels[this.targetType] || []
        },
    },
    methods: {
        ...mapMutations("offPanel", ["closeOffPanel"]),
        ...mapMutations("bulk", ["deselectAllForBulkAction"]),
        ...mapActions("bulk", ["bulkAction"]),
        ...mapMutations("labels", ["setLabels"]),
        ...mapActions("labels", ["fetchLabels"]),
        onOpenMergePanel() {
            this.labelMergeDestination = _.assign({}, EMPTY_LABEL, {
                target_type: this.targetType,
                order: 0,
            })
            setTimeout(() => {
                this.vuelidate = this.$refs.labelForm.$v
            })
        },
        mergeLabels() {
            return $httpX({
                name: `mergeLabels`,
                commit: this.$store.commit,
                url: urls.labelsMerge,
                method: "POST",
                data: {
                    ids_to_merge: this.bulkActionSelectionAsList,
                    destination: this.labelMergeDestination,
                },
            }).then((response) => {
                this.setLabels({
                    targetType: this.targetType,
                    labels: response.data,
                })
                this.deselectAllForBulkAction()
                setTimeout(() => this.closeOffPanel("labelsMerge"), 1000)
            })
        },
        bulkDelete() {
            this.bulkAction({
                url: urls.labelsBulkAction,
                action: "delete",
            }).then(() => {
                this.fetchLabels(this.targetType)
            })
        },
        cancelDeletion() {
            this.deletionRequested = false
        },
    },
    i18n: {
        messages: {
            fr: {
                merge: "Fusionner",
                action: {
                    delete: "Supprimer",
                    merge: "Fusionner",
                },
                areYouSureDeletion:
                    "Vous allez supprimer 1 label, êtes vous sûr ? | Vous allez supprimer {count} labels, êtes vous sûr ? ",
            },
            en: {
                merge: "Merge",
                action: {
                    delete: "Delete",
                    merge: "Merge",
                },
                areYouSureDeletion:
                    "1 label will be deleted, are you sure ? | {count} labels will be deleted, are you sure ?  ",
            },
        },
    },
}
</script>

<style lang="scss">
.LabelsListBulkbar {
    @apply sticky top-0 bg-gray-50 py-2 border-b-2 border-gray-300;

    // Align exactly the checkbox with those into the list
    .BulkBar {
        margin-left: 26px;
    }
    margin-bottom: 10px;
}
</style>
