<template>
<MainLayout>
    <template #title>
        {{ $t("workflowStates") }}
    </template>

    <template #actions>
        <AdminButton @click="startWorkflowStateCreation()">
            {{ $t("addWorkflowState") }}
        </AdminButton>
    </template>

    <template #content>
        <div class="container mx-auto p-5">
            <Loadarium name="fetchWorkflowStates">
                <AdminList
                    :instancesList="workflowStates"
                    :sortable="true"
                    @delete="deleteWorkflowState"
                    @edit="$refs.form.openFormPanel($event)"
                    @sorted="onStatesSorted"
                >
                    <template slot-scope="{ instance }">
                        <div
                            class="color-swatch"
                            :style="{ 'background-color': instance.color }"
                        />
                        {{ instance.label }}
                    </template>
                </AdminList>

                <div
                    v-if="workflowStates && workflowStates.length == 0"
                    class="help-text"
                >
                    <div class="help-text-title">{{ $t("noWorkflowState") }}</div>
                    <div class="help-text-content">
                        {{ $t("explainWorkflow") }}
                    </div>
                </div>
            </Loadarium>

            <AutoFormInPanel
                name="workflowStateForm"
                ref="form"
                :saveUrl="urls.workflowStates"
                :schema="workflowStateFormSchema"
                :title="$t('addWorkflowState')"
                @created="onWorkflowStateCreated"
                @updated="onWorkflowStateUpdated"
            />
        </div>
    </template>
</MainLayout>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { EVENTS, dispatchEvent } from "@js/events"
import PilotMixin from "@components/PilotMixin"
import MainLayout from "@components/layout/MainLayout"
import AdminButton from "@components/admin/AdminButton"
import AdminList from "@components/admin/AdminList.vue"

export default {
    name: "WorkflowStateAdminApp",
    mixins: [PilotMixin],
    components: {
        AdminButton,
        AdminList,
        MainLayout,
    },
    computed: {
        ...mapState("workflow", ["workflowStates"]),
        workflowStateFormSchema() {
            return [
                {
                    name: "label",
                    type: "char",
                    label: this.$t("name"),
                    placeholder: this.$t("name"),
                    required: true,
                },
                {
                    name: "color",
                    type: "color",
                    label: this.$t("color"),
                    inputType: "background",
                    required: true,
                },
            ]
        },
    },
    methods: {
        ...mapMutations("workflow", [
            "appendToWorkflowStates",
            "updateWorkflowState",
            "setWorkflowStates",
        ]),
        ...mapActions("workflow", [
            "fetchWorkflowStates",
            "deleteWorkflowState",
            "setWorkflowStatesOrder",
        ]),
        onWorkflowStateCreated(workflowState) {
            this.appendToWorkflowStates(workflowState)
            dispatchEvent(EVENTS.workflowStateCreated, workflowState)
        },
        onWorkflowStateUpdated(workflowState) {
            this.updateWorkflowState(workflowState)
            dispatchEvent(EVENTS.workflowStateUpdated, workflowState)
        },
        startWorkflowStateCreation() {
            this.$refs.form.openFormPanel({
                order: this.workflowStates.length,
            })
        },
        onStatesSorted(newStates) {
            let newWorkflowStatesOrder = newStates.map((state, index) => ({
                id: state.id,
                order: index,
            }))

            // Consider the new ordering will be accepted by the backend.
            // This is to prevent the element to flicker when waiting the response from the backend
            this.setWorkflowStates(newWorkflowStatesOrder)

            // Ask the backend to actually save the new order
            // It will respond with the current state of the label order, which should be the same than ours.
            this.setWorkflowStatesOrder(newWorkflowStatesOrder)
        },
    },
    created() {
        this.fetchWorkflowStates()
    },
    i18n: {
        messages: {
            fr: {
                addWorkflowState: "Ajouter un état de workflow",
                explainWorkflow:
                    "Le workflow permet de définir les différents status possibles d'un contenu",
                noWorkflowState: "Aucun état de workflow",
            },
            en: {
                addWorkflowState: "Add workflow state",
                explainWorkflow: "The workflow defines the different states of a content",
                noWorkflowState: "No workflow state",
            },
        },
    },
}
</script>
