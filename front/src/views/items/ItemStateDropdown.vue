<template>
<Popper
    ref="popper"
    :appendToBody="appendToBody"
    boundariesSelector="main"
    :placement="placement"
    :preventCloseCallback="preventCloseCallback"
    triggerElementName="PopperRef"
    triggerType="click"
    :visibleArrow="false"
    @show="onShowPopper"
>
    <template #triggerElement>
        <button
            class="button bg-gray-cool-50"
            :class="referenceClass"
            ref="PopperRef"
        >
            <ItemState
                :showStateText="showStateText"
                :state="item.workflow_state"
            />
        </button>
    </template>

    <template #content>
        <div
            class="ItemStateDropdown__menu"
            ref="ItemStateDropdown"
        >
            <transition>
                <!-- State list panel -->
                <div
                    v-if="!isStateSavePanelOpen"
                    class="ItemStateDropdown__stateListPanel"
                    key="stateListPanel"
                >
                    <div class="flex items-center justify-between mb-5">
                        <div class="font-black">{{ $t("workflowStates") }}</div>
                        <button
                            class="button is-small"
                            @click="closeDropDown"
                        >
                            {{ $t("close") }}
                        </button>
                    </div>
                    <div
                        v-for="stateChoice in workflowStates"
                        class="ItemStateDropdown__stateListPanel__state"
                        :class="stateChoice.id == itemWorkflowStateId ? 'active' : 'text-gray-400'"
                        :key="stateChoice.id"
                        @click="openStateSavePanel(stateChoice)"
                        @mouseleave="hoveredStateChoice = null"
                        @mouseover="hoveredStateChoice = stateChoice"
                    >
                        <div v-if="stateChoice.id == itemWorkflowStateId">
                            <ItemState :state="stateChoice" />
                        </div>
                        <div v-else>
                            <ItemState
                                v-if="hoveredStateChoice == stateChoice"
                                key="hover"
                                :state="stateChoice"
                            />
                            <ItemState
                                v-else
                                key="notHover"
                                :muted="true"
                                :state="stateChoice"
                            />
                        </div>
                    </div>
                </div>
                <!-- END State list panel -->

                <!-- State save panel -->
                <div
                    v-else
                    class="ItemStateDropdown__stateSavePanel"
                    key="stateSavePanel"
                >
                    <div class="text-lg font-black">
                        {{ $t("commentTitle") }}
                        <span
                            class="border-b-4"
                            :style="{ 'border-bottom-color': currentStateChoice.color }"
                        >
                            {{ currentStateChoice.label }}
                        </span>
                    </div>

                    <transition
                        enter-active-class="animated animated-150 fadeIn"
                        leave-active-class="animated animated-150 fadeOut"
                        mode="out-in"
                    >
                        <a
                            v-if="!isCommentEditorVisible"
                            class="text-gray-500 font-medium underline hover:text-blue-700"
                            @click="startComment"
                            @focus="startComment"
                        >
                            {{ $t("addComment") }}
                        </a>
                        <CommentBox
                            v-else
                            v-model="comment"
                            class="ItemStateDropdown__state SavePanel__commentbox border border-gray-300 rounded my-2"
                            ref="commentEditor"
                            :contentType="contentTypes.Item"
                            :inactiveMentionGroups="inactiveMentionGroups"
                            :placeholder="$t('commentPlaceholder')"
                        />
                    </transition>

                    <div class="flex flex-col">
                        <SmartButtonSpinner
                            class="ItemStateDropdown__saveButton button is-blue w-full"
                            name="saveStateAndComment"
                            @click="saveStateAndComment()"
                        >
                            <span class="inline-flex flex-col">
                                {{ $t("changeStatusTo") }}
                            </span>
                        </SmartButtonSpinner>

                        <button
                            class="button w-full"
                            @click="closeStateSavePanel()"
                        >
                            {{ $t("cancel") }}
                        </button>
                    </div>
                </div>
                <!-- END State save panel -->
            </transition>
        </div>
    </template>
</Popper>
</template>

<script>
import $ from "jquery"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { initialDataPromise } from "@js/bootstrap"
import { $httpX } from "@js/ajax.js"
import urls from "@js/urls.js"
import { waitUntil } from "@js/utils"
import PilotMixin from "@components/PilotMixin"

import CommentBox from "@components/CommentBox.vue"
import ItemState from "./ItemState.vue"

export default {
    name: "ItemStateDropdown",
    mixins: [PilotMixin],
    components: {
        CommentBox,
        ItemState,
    },
    props: {
        item: Object,
        showStateText: {
            type: Boolean,
            default: true,
        },
        inactiveMentionGroups: Object,
        placement: {
            type: String,
            default: "bottom",
        },
        truncate: {
            type: Boolean,
            default: false,
        },
        referenceClass: String,
        /**
         * Allow to move the popper DOM element at the end of #app.
         * This may help with issues, such as sticky + z-index ( ex: RichTextMenuBar )
         */
        appendToBody: {
            type: Boolean,
            default: false,
        },
    },
    data: () => ({
        isStateSavePanelOpen: false,
        currentStateChoice: null,
        comment: null,
        hoveredStateChoice: false,
        isCommentEditorVisible: false,
    }),
    computed: {
        ...mapState("workflow", ["workflowStates"]),
        itemWorkflowStateId() {
            return this.item.workflow_state && this.item.workflow_state.id
        },
    },
    methods: {
        ...mapMutations("loading", ["resetLoading"]),
        nailDropdown() {
            if (!this.workflowStates || !this.workflowStates.length) {
                return
            }
            this.$nextTick(() => {
                if (!this.$refs.popper) {
                    return
                }
                // Fix the height of the popper so it won't flicker when changing the panel
                let $dropdown = $(this.$refs.ItemStateDropdown)
                let height = Math.max($dropdown.height(), 350)
                $dropdown.css("min-height", height).css("height", height)
                // Final positioning of the popper after the state choices are loaded.
                this.$refs.popper.updatePopper()
            })
        },
        closeDropDown() {
            if (this.$refs.popper) {
                this.$refs.popper.hidePopper()
            }
            this.closeStateSavePanel()
        },
        openStateSavePanel(stateChoice) {
            if (stateChoice.id == this.itemWorkflowStateId) {
                return
            }

            this.comment = null
            this.currentStateChoice = stateChoice
            this.isStateSavePanelOpen = true
        },
        closeStateSavePanel() {
            this.currentStateChoice = null
            this.isStateSavePanelOpen = false
            this.isCommentEditorVisible = false
            this.resetLoading("saveStateAndComment")
        },
        saveStateAndComment() {
            if (!this.currentStateChoice) {
                return
            }

            $httpX({
                name: "saveStateAndComment",
                commit: this.$store.commit,
                url: urls.itemUpdateWorkflowState.format({ id: this.item.id }),
                method: "PATCH",
                data: {
                    workflow_state_id: this.currentStateChoice.id,
                    comment: this.comment,
                },
            }).then((response) => {
                this.$emit("saved", response.data)
                this.closeDropDown()
            })
        },
        preventCloseCallback(event) {
            // click is on the @mentions autocomplete
            return (
                $(event.target).closest(".CommentBox").length ||
                $(event.target).closest(".CommentBox__mentionsDropdown").length
            )
        },
        startComment() {
            this.isCommentEditorVisible = true

            waitUntil(
                () => this.$refs.commentEditor && this.$refs.commentEditor.editor,
                () => this.$refs.commentEditor.editor.focus(),
            )
        },
        onShowPopper() {
            this.nailDropdown()
        },
    },
    created() {
        // Wait for the workflow state list to be loaded, then recompute the popper height & position.
        initialDataPromise.then(this.nailDropdown)
    },
    i18n: {
        messages: {
            fr: {
                addComment: "Associer un commentaire au changement de statut",
                status: "Statut : ",
                mark: "Marquer : ",
                commentTitle: "Confirmer le changement de statut vers",
                commentPlaceholder: "Votre commentaire .. (@mention possible)",
                changeStatusTo: "Confirmer",
            },
            en: {
                status: "Status:",
                mark: "Mark:",
                commentTitle: "Confirm",
                commentPlaceholder: "Your comment.. (@mention possible)",
                changeStatusTo: "Change status to",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/include_media.scss";
@import "~@sass/colors.scss";

$border: solid 1px $gray-light;
$panel-transition: all 0.15s linear;

@mixin left-panel-animation() {
    /* Animations */
    &.v-enter-active,
    &.v-leave-active {
        transition: $panel-transition;
    }
    &.v-enter,
    &.v-leave-to {
        position: absolute;
        transform: translateX(-99%);
    }
}

@mixin right-panel-animation() {
    /* Animations */
    &.v-enter-active,
    &.v-leave-active {
        transition: $panel-transition;
    }
    &.v-enter,
    &.v-leave-to {
        position: absolute;
        transform: translateX(100%);
    }
}

.ItemStateDropdown__menu {
    overflow: hidden;
    width: 340px;
    max-width: 340px;
    padding: 0;
    position: relative;
}

.ItemStateDropdown__menu.left {
    right: 0;
    left: auto;
}

.ItemStateDropdown__menu.right {
    right: auto;
    left: 0;
}

.ItemStateDropdown__stateListPanel {
    @include left-panel-animation();
    text-align: left;
    padding: 0;
}

.ItemStateDropdown__stateListPanel__state {
    cursor: pointer;
    @apply p-2 text-gray-500 rounded border border-gray-100 mb-1;

    &.active,
    &:hover {
        @apply bg-gray-100 text-gray-900 border-gray-200;
    }
}

.ItemStateDropdown__stateSavePanel {
    @include right-panel-animation();
    @apply h-full flex flex-col justify-evenly overflow-y-auto overflow-x-hidden;
}

.ItemStateDropdown__saveButton {
    @apply leading-snug h-auto py-2 my-4 #{!important};
}
</style>
