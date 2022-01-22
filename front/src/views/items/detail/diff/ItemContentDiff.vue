<template>
<div class="ItemContentDiff">
    <div class="flex font-bold sticky top-0 z-50 bg-yellow-100 p-2">
        <div class="w-1/2">{{ $t("before") }} ( V{{ itemReadOnly.diffVersions.left }} )</div>
        <div class="w-1/2 ml-2 flex justify-between flex-wrap">
            <span>{{ $t("after") }} ( V{{ itemReadOnly.diffVersions.right }} )</span>

            <!-- Hide diff -->
            <!-- .stop needed on @click to prevent version loading -->
            <button
                class="button is-orange is-xsmall"
                @click.stop="exitDiffMode()"
            >
                {{ $t("hideDiffWithPreviousVersion") }}
            </button>
        </div>
    </div>

    <template v-for="fieldSchema in itemReadOnly.contentSchema">
        <div class="flex mt-6">
            <div class="form__field__label w-1/2">
                {{ fieldSchema.label }}
            </div>
            <div class="form__field__label w-1/2 ml-2">
                {{ fieldSchema.label }}
            </div>
        </div>

        <p v-if="getFieldDiff(fieldSchema).message">
            <em class="text-gray-600 text-sm">{{ getFieldDiff(fieldSchema).message }}</em>
        </p>

        <ItemContentDiffProsemirrorField
            v-if="fieldSchema.is_prosemirror"
            :fieldSchema="fieldSchema"
            :itemReadOnly="itemReadOnly"
        />
        <ItemContentDiffField
            v-else
            :fieldSchema="fieldSchema"
            :itemReadOnly="itemReadOnly"
        />
    </template>
</div>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import ItemContentDiffField from "./ItemContentDiffField"
import ItemContentDiffProsemirrorField from "./ItemContentDiffProsemirrorField"

export default {
    name: "ItemContentDiff",
    mixins: [PilotMixin],
    components: {
        ItemContentDiffField,
        ItemContentDiffProsemirrorField,
    },
    props: {
        fieldSchema: Object,
        itemReadOnly: Object,
    },
    methods: {
        ...mapActions("itemDetail", ["exitDiffMode"]),
        getFieldDiff(fieldSchema) {
            return this.itemReadOnly.fieldDiffs[fieldSchema.name]
        },
    },
    i18n: {
        messages: {
            fr: {
                after: "Après",
                before: "Avant",
                hideDiffWithPreviousVersion: "Masquer les différences",
            },
            en: {
                after: "After",
                before: "Before",
                hideDiffWithPreviousVersion: "Hide the differences",
            },
        },
    },
}
</script>

<style lang="scss">
.ItemContentDiff__panels {
    @apply flex;
}

.ItemContentDiff__panel {
    flex-grow: 1;
    flex-shrink: 0;
    // set a width (any width), so the panels won't flickr.
    // flex-grow will then grow the panel as necesary.
    width: 1px;
}
</style>
