<template>
<div class="ItemContentMergeTool">
    <div class="sticky top-0 z-50 flex bg-yellow-100 p-4">
        <div class="pl-4 w-2/5">
            V{{ editSessionForMergeTool.version }}
            <div
                v-for="editor in editSessionForMergeTool.editors"
                class="text-gray-600 text-sm"
            >
                <UserDisplay
                    v-if="editor && editor.id"
                    :user="editor"
                    :withAvatar="true"
                    :withUsername="true"
                />
                <template v-else>{{ editor }}</template>
            </div>
        </div>
        <div class="pl-4 w-2/5">
            {{ $t("mergeResult") }}
        </div>
        <div class="pl-4 w-1/5">
            <button
                class="button is-blue"
                :disabled="!hasChanges"
                @click="doMerge"
            >
                {{ $t("validateMerge") }}
            </button>
            <button
                class="button is-orange"
                @click="closePanel"
            >
                {{ $t("cancel") }}
            </button>
        </div>
    </div>

    <div class="p-4">
        <template v-for="fieldSchema in allFieldSchemas">
            <div class="flex mt-2">
                <div class="form__field__label w-2/5">
                    {{ fieldSchema.label }}
                </div>
                <div class="form__field__label w-2/5 ml-2">
                    {{ fieldSchema.label }}
                </div>
            </div>

            <ItemMergeProsemirrorField
                v-if="fieldSchema.is_prosemirror"
                :fieldSchema="fieldSchema"
                @mergeChange="onMergeChange"
            />
            <ItemMergeField
                v-else
                :fieldSchema="fieldSchema"
                @mergeChange="onMergeChange"
            />
        </template>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import Vue from "vue"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import ItemMergeField from "./ItemMergeField"
import ItemMergeProsemirrorField from "./ItemMergeProsemirrorField"

export default {
    name: "ItemContentMergeTool",
    mixins: [PilotMixin],
    components: {
        ItemMergeField,
        ItemMergeProsemirrorField,
    },
    data: () => ({
        mergeChanges: {},
    }),
    computed: {
        ...mapState("itemDetail", ["item", "editSessionForMergeTool"]),
        ...mapState("itemContentForm", ["itemEditable"]),
        ...mapGetters("itemContentForm", ["allFieldSchemas"]),
        hasChanges() {
            return Object.keys(this.mergeChanges).length > 0
        },
    },
    methods: {
        ...mapActions("itemDetail", ["closePanel"]),
        ...mapMutations("itemContentForm", ["setItemContentField", "addPendingChange"]),
        ...mapActions("itemContentForm", ["saveItemContentRT"]),
        onMergeChange(change) {
            let fieldName = change.fieldName
            let currentValue = this.itemEditable.content[fieldName]
            if (_.isEqual(change.value, currentValue)) {
                Vue.delete(this.mergeChanges, fieldName)
            } else {
                Vue.set(this.mergeChanges, fieldName, change)
            }
        },
        doMerge() {
            if (!this.hasChanges) {
                return
            }
            for (let fieldName in this.mergeChanges) {
                this.setItemContentField(this.mergeChanges[fieldName])
                this.addPendingChange(this.mergeChanges[fieldName])
            }
            this.saveItemContentRT()
            this.closePanel()
        },
    },
    i18n: {
        messages: {
            fr: {
                mergeResult: "Résultat de fusion",
                validateMerge: "Valider les modifications",
            },
            en: {
                mergeResult: "Merge result",
                validateMerge: "Validate merge",
            },
        },
    },
}
</script>

<style lang="scss">
.ItemContentMergeTool {
    @apply bg-white flex-auto overflow-y-auto;
}

.ItemContentMergeTool__panels {
    @apply flex;
}

.ItemContentMergeTool__panel {
    flex-grow: 1;
    flex-shrink: 0;
    // set a width (any width), so the panels won't flickr.
    // flex-grow will then grow the panel as necesary.
    width: 1px;
}
</style>
