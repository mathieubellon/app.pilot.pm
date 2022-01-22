<template>
<div class="TargetPicker">
    <div class="flex items-center">
        <VueFuse
            class="flex-grow"
            :defaultAll="true"
            :keys="['name']"
            :list="targets"
            :placeholder="$t('search')"
            :threshold="0.1"
            @result="onFuseResult"
        />
        <template v-if="multiple">
            <ButtonSpinner
                class="button is-small is-outlined mx-2"
                :disabled="pickedTargetsId.length == targets.length"
                :isLoading="loading && lastSelection == 'pickAll'"
                @click="pickAll"
            >
                {{ $t("selectAll") }}
            </ButtonSpinner>

            <ButtonSpinner
                class="button is-small is-outlined"
                :disabled="pickedTargetsId.length == 0"
                :isLoading="loading && lastSelection == 'unpickAll'"
                @click="unpickAll"
            >
                {{ $t("deselectAll") }}
            </ButtonSpinner>
        </template>
    </div>

    <div class="Picker__List">
        <div
            v-for="target in filteredTargets"
            class="Picker__ElementWrapper"
        >
            <div
                v-if="loading && lastSelection == target"
                class="Picker__Loader"
            >
                <BarLoader
                    color="#3182CE"
                    :loading="true"
                    :width="100"
                    widthUnit="%"
                />
            </div>
            <TargetPickerElement
                v-else
                :disabled="loading"
                :key="target.id"
                :picked="isPicked(target)"
                :target="target"
                @pick="onPick"
            />
        </div>
    </div>

    <div
        v-if="targets.length == 0"
        class="help-text"
    >
        <div class="help-text-title">
            <Icon
                class="help-text-icon"
                name="Target"
            />
            <span>{{ $t("noTargetYet") }}</span>
        </div>
        <SmartLink
            class="button is-blue"
            :to="urls.targetsApp.url"
        >
            {{ $t("createTarget") }}
        </SmartLink>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import PilotMixin from "@components/PilotMixin"

import TargetPickerElement from "./TargetPickerElement.vue"
import ButtonSpinner from "@components/ButtonSpinner"

export default {
    name: "TargetPicker",
    mixins: [PilotMixin],
    components: {
        TargetPickerElement,
        ButtonSpinner,
    },
    props: {
        multiple: Boolean,
        targets: Array,
        pickedTarget: Object,
        pickedTargetsId: Array,
        loading: Boolean,
    },
    data: () => ({
        filteredTargets: [],
        lastSelection: null,
    }),
    methods: {
        onFuseResult(filteredTargets) {
            this.filteredTargets = filteredTargets
        },
        onPick(target) {
            this.lastSelection = target
            if (this.multiple) {
                // Toggle value in array (https://gist.github.com/uhtred/ec64752a8e9c9b83922b3ebb36e3ac23)
                this.$emit("pick", _.xor(this.pickedTargetsId, [target.id]))
            } else {
                this.$emit("pick", target)
            }
        },
        pickAll() {
            this.lastSelection = "pickAll"
            this.$emit(
                "pick",
                this.targets.map((target) => target.id),
            )
        },
        unpickAll() {
            this.lastSelection = "unpickAll"
            this.$emit("pick", [])
        },
        isPicked(target) {
            if (this.multiple) {
                return _.includes(this.pickedTargetsId, target.id)
            } else {
                return this.pickedTarget && this.pickedTarget.id == target.id
            }
        },
    },
    i18n: {
        messages: {
            fr: {
                createTarget: "Créer une cible",
                noTargetYet: "Vous n'avez pas encore créé de cible",
            },
            en: {
                createTarget: "Create a target",
                noTargetYet: "You haven't created any target yet",
            },
        },
    },
}
</script>
