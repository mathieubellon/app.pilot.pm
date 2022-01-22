<template>
<Popper
    ref="LabelSelectPopper"
    :boundariesSelector="boundariesSelector"
    :placement="placement"
    :triggerElementName="triggerElementName"
    triggerType="click"
    :visibleArrow="false"
    @show="onShow"
>
    <template #triggerElement>
        <slot name="triggerElement" />
    </template>

    <template #content>
        <div class="LabelSelect">
            <VueFuse
                class="LabelSelect__labelInput w-full mb-2"
                ref="labelInput"
                :defaultAll="true"
                inputType=""
                :keys="['name']"
                :list="labels"
                :placeholder="$t('search')"
                :shouldSort="false"
                :threshold="0.1"
                @input="onFuseInput"
                @result="onFuseResult"
            />

            <div
                v-if="labelInputValue"
                class="mt-3"
            >
                <span
                    v-if="!filteredLabels.length"
                    class="mr-2"
                >
                    {{ $t("noResults") }}
                </span>
                <Loadarium
                    name="createLabel"
                    errorLabel=""
                >
                    <a
                        class="text-sm font-medium"
                        @click="createLabelFromInput"
                    >
                        {{ $t("create") }} "{{ labelInputValue }}"
                    </a>
                </Loadarium>
            </div>

            <Loadarium name="fetchLabels">
                <div
                    v-if="labels.length == 0"
                    class="LabelsListEmpty"
                >
                    {{ $t("emptyListPlaceholder") }}
                </div>

                <SlickList
                    v-else-if="sortable"
                    class="LabelSelect__optionList"
                    axis="y"
                    :distance="5"
                    helperClass="LabelSelect__SortableHelper"
                    lockAxis="y"
                    :lockToContainerEdges="true"
                    :useDragHandle="true"
                    :value="filteredLabels"
                    @input="onLabelsSorted"
                >
                    <SlickItem
                        v-for="(label, labelIndex) in filteredLabels"
                        class="LabelSelect__option h-10"
                        :index="labelIndex"
                        :key="label.id"
                    >
                        <BarLoader v-if="isUpdating && lastLabelClicked == label" />
                        <template v-else>
                            <span
                                class="LabelSelect__reorderHandle"
                                v-handle
                            >
                                <Icon name="MoveHandle" />
                            </span>
                            <span
                                class="LabelSelect__option__label"
                                @click="selectLabel(label)"
                            >
                                <Label :label="label" />
                            </span>

                            <LabelSelectEditionPopper :label="label" />
                        </template>
                    </SlickItem>
                </SlickList>

                <div
                    v-else
                    class="LabelSelect__optionList mt-5"
                >
                    <div
                        v-for="label in filteredLabels"
                        class="LabelSelect__option mb-2 h-10"
                        :class="{ 'bg-gray-200': isSelected(label) }"
                        :key="label.id"
                    >
                        <BarLoader v-if="isUpdating && lastLabelClicked == label" />
                        <template v-else>
                            <div
                                class="LabelSelect__option__label"
                                @click="selectLabel(label)"
                            >
                                <BarLoader v-if="isUpdating && lastLabelClicked == label" />
                                <Label
                                    v-else
                                    :label="label"
                                />
                            </div>

                            <a
                                v-if="isSelected(label)"
                                class="button is-small mr-3"
                                @click="removeLabel(label)"
                            >
                                {{ $t("remove") }}
                            </a>
                            <a
                                v-else
                                class="button is-small mr-3"
                                @click="selectLabel(label)"
                            >
                                {{ $t("add") }}
                            </a>

                            <LabelSelectEditionPopper :label="label" />
                        </template>
                    </div>
                </div>
            </Loadarium>
        </div>
    </template>
</Popper>
</template>

<script>
import _ from "lodash"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { sortByAlphaString } from "@js/utils.js"
import PilotMixin from "@components/PilotMixin"

import { SlickList, SlickItem, HandleDirective } from "vue-slicksort"

import Label from "./Label.vue"
import LabelSelectEditionPopper from "./LabelSelectEditionPopper.vue"
import { DEFAULT_LABEL_BG_COLOR, DEFAULT_LABEL_COLOR } from "@/store/modules/LabelStore"

export default {
    name: "LabelSelect",
    mixins: [PilotMixin],
    components: {
        SlickList,
        SlickItem,

        Label,
        LabelSelectEditionPopper,
    },
    directives: { handle: HandleDirective },
    props: {
        value: [Object, Array],
        targetType: {
            type: String,
            required: true,
        },
        multiple: {
            type: Boolean,
            default: true,
        },
        sortable: {
            type: Boolean,
            default: true,
        },
        placement: {
            type: String,
            default: "right",
        },
        isUpdating: {
            type: Boolean,
            default: false,
        },
        boundariesSelector: String,
        triggerElementName: {
            type: String,
            required: true,
        },
    },
    data: () => ({
        labelInputValue: "",
        filteredLabels: [],
        lastLabelClicked: null,
    }),
    computed: {
        labels() {
            let labels = this.$store.state.labels.labels[this.targetType] || []
            // If the drag'n'drop is disabled, the order is not defined by the user,
            // but we sort the labels alphabetically
            if (!this.sortable) {
                labels = sortByAlphaString(labels, (label) => label.name)
            }
            return labels
        },
        selectedLabels() {
            return this.multiple ? this.value : this.value ? [this.value] : []
        },
    },
    methods: {
        ...mapMutations("loading", ["resetLoading"]),
        ...mapMutations("labels", ["setLabels"]),
        ...mapActions("labels", ["fetchLabels", "createLabel", "setLabelsOrder"]),
        selectLabel(label) {
            this.lastLabelClicked = label

            if (this.multiple) {
                // Only emit if the label isn't already in the list
                if (!_.find(this.value, (l) => l.id == label.id)) {
                    this.$emit("input", _.concat(this.value, label))
                }
            } else {
                // Only emit if the label isn't already selected
                if (!this.value || label.id != this.value.id) {
                    this.$emit("input", label)
                }
            }
            // If it's a single-select label, we can now close the popper
            if (!this.multiple) {
                this.$refs.LabelSelectPopper.hidePopper()
            }
            // Else, it's a multiple select label, the popper stay open.
            // We need to recompute the popper position when a label is added, because it may increase its height
            else {
                this.$refs.LabelSelectPopper.updatePopper()
            }
        },
        isSelected(label) {
            const look = _.findIndex(this.selectedLabels, ["id", label.id])
            return look > -1
        },
        removeLabel(label) {
            this.lastLabelClicked = label

            if (this.multiple) {
                this.$emit(
                    "input",
                    this.value.filter((l) => l.id != label.id),
                )
            } else {
                this.$emit("input", null)
            }
        },
        createLabelFromInput() {
            this.createLabel({
                name: this.labelInputValue,
                target_type: this.targetType,
                order: this.labels.length,
                color: DEFAULT_LABEL_COLOR,
                background_color: DEFAULT_LABEL_BG_COLOR,
            }).then((label) => {
                this.$refs.labelInput.search = ""
                this.selectLabel(label)
            })
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
        onFuseInput(labelInputValue) {
            this.labelInputValue = labelInputValue
            this.resetLoading("createLabel")
        },
        onFuseResult(filteredLabels) {
            this.filteredLabels = filteredLabels
        },
        onShow() {
            // Fetch the labels on the first opening, if the're not already fetched
            this.fetchLabels(this.targetType)
                // We need to recompute the popper position when the label list is loaded
                .then(() => this.$refs.LabelSelectPopper.updatePopper())
        },
    },
    created() {
        if (this.multiple && !_.isArray(this.value)) {
            throw Error("LabelSelect with multiple=true must use an array value")
        }
        if (!this.multiple && !_.isObject(this.value) && !_.isNil(this.value)) {
            throw Error("LabelSelect with multiple=false must use a label object value")
        }
    },
    i18n: {
        messages: {
            fr: {
                emptyListPlaceholder:
                    "Cette liste est vide. Saisissez un premier terme dans la zone de recherche pour créer un élément",
            },
            en: {
                emptyListPlaceholder:
                    "This list is empty. Start typing in the search bar to create an element.",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.LabelsListEmpty {
    @apply text-gray-800 text-sm font-medium mt-5;
}

.LabelSelect {
    width: 500px;
    padding: 1em;

    /** Prevent text selection for drag */
    user-select: none;

    a {
        text-decoration: none;
    }
}

.LabelSelect__selection {
    flex-grow: 1;
    display: flex;
    flex-flow: row wrap;
    width: 100%;
    margin-bottom: 1em;
}

.LabelSelect__selectionLabel {
    display: flex;
    justify-content: space-around;
    align-items: center;
    margin: 0.1em;
}

.LabelSelect__labelInput {
    flex-grow: 1;
    min-width: 150px;

    background-color: $gray-lighter;
    //margin-left: 5px;
    padding: 0.4em;
    border-radius: 4px;
    font-size: 1.1em;
    border: none;

    // This is for Chrome
    &:focus {
        outline: none;
    }
}

.LabelSelect__optionList {
    max-height: 400px;
    overflow-y: auto;
    overflow-x: hidden;
}

.LabelSelect__option {
    padding: 3px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: space-between;

    &:hover {
        background: $gray-lighter;
    }
}

.LabelSelect__option__label {
    flex-grow: 1;
    cursor: pointer;
    display: flex;
    align-items: center;
}

.LabelSelect__SortableHelper {
    // Above Popper (which is 100)
    z-index: 110;
}

.LabelSelect__reorderHandle {
    font-size: 20px;
    padding: 3px 6px 3px 3px;
    color: $gray-dark;
    cursor: grab;
}
</style>
