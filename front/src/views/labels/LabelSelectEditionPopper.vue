<template>
<Popper
    ref="LabelSelectEditionPopper"
    boundariesSelector="body"
    placement="bottom"
    triggerElementName="PopperRef"
    triggerType="click"
    @show="onShow"
>
    <template #triggerElement>
        <div ref="PopperRef">
            <a class="button is-small text-gray-600">
                {{ $t("edit") }}
            </a>
        </div>
    </template>

    <template #content>
        <div class="text-gray-900 font-semibold text-sm">
            {{ $t("label") }}
            <span class="text-gray-500">{{ $t("editPossible") }}</span>
        </div>
        <input
            v-model="name"
            class="bg-gray-200 mb-4"
            type="text"
        />
        <div class="text-gray-900 font-semibold text-sm">{{ $t("color") }}</div>
        <ColorPickerCurated
            v-model="labelColors"
            class="shadow shadow-inner"
        />
        <div class="mt-4">
            <Deletarium
                loadingName="deleteLabel"
                @delete="deleteLabel(label)"
                @deletionRequested="$refs.LabelSelectEditionPopper.updatePopper()"
            >
                <SmartButtonSpinner
                    class="is-blue"
                    name="partialUpdateLabel"
                    @click="onSaveClick"
                >
                    {{ $t("save") }}
                </SmartButtonSpinner>
            </Deletarium>
        </div>
    </template>
</Popper>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import ColorPickerCurated from "@components/ColorPickerCurated"

export default {
    name: "LabelSelectEditionPopper",
    mixins: [PilotMixin],
    components: {
        ColorPickerCurated,
    },
    props: {
        label: Object,
    },
    data: () => ({
        name: "",
        labelColors: {
            color: null,
            backgroundColor: null,
        },
    }),
    methods: {
        ...mapMutations("loading", ["resetLoading"]),
        ...mapActions("labels", ["partialUpdateLabel", "deleteLabel"]),
        onShow() {
            this.resetLoading("partialUpdateLabel")
            this.resetLoading("deleteLabel")
            this.name = this.label.name
            this.labelColors.color = this.label.color
            this.labelColors.backgroundColor = this.label.background_color
        },
        onSaveClick() {
            this.partialUpdateLabel({
                id: this.label.id,
                name: this.name,
                color: this.labelColors.color,
                background_color: this.labelColors.backgroundColor,
            }).then(() => {
                this.$refs.LabelSelectEditionPopper.hidePopper()
            })
        },
    },
}
</script>
