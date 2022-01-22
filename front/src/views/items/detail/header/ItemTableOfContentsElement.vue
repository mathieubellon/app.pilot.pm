<template>
<a
    class="inline-flex items-center justify-between mt-2 font-medium text-sm bg-gray-50 hover:bg-gray-100 px-2 rounded"
    :class="{
        'bg-red-100': hasError,
        'bg-yellow-100': hasWarning,
    }"
    @click="scrollToField"
>
    <div class="w-full">
        <div class="text-black">{{ fieldSchema.label }}</div>
        <ValidationErrors
            v-if="hasError"
            :showOnlyWhenDirty="false"
            :validation="errorValidation"
        />
        <ValidationWarnings
            v-if="hasWarning"
            :showOnlyWhenDirty="false"
            :warnings="warningValidation"
        />

        <template v-if="fieldSchema.is_prosemirror">
            <div
                v-for="(headingNode, headingIndex) in headingNodes"
                class="hover:underline w-full text-xs"
                @click.stop="scrollToHeading(headingIndex)"
            >
                h{{ headingNode.attrs.level }}
                {{ "-".repeat(headingNode.attrs.level) }}
                {{ headingNode.content[0].text }}
            </div>
        </template>
    </div>
    <Icon
        name="Eye"
        size="18px"
    />
</a>
</template>

<script>
import $ from "jquery"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

import { getHeadingNodes } from "@richText/utils"

import { scrollItemTo } from "@js/items/itemsUtils"

export default {
    name: "ItemTableOfContentsElement",
    mixins: [PilotMixin],
    props: {
        fieldSchema: Object,
    },
    computed: {
        ...mapState("itemContentForm", ["validation", "warnings"]),
        ...mapState("itemContentForm", ["itemEditable", "tiptapEditors"]),
        errorValidation() {
            return this.validation.content[this.fieldSchema.name]
        },
        warningValidation() {
            return this.warnings.content[this.fieldSchema.name]
        },
        hasError() {
            return this.errorValidation && this.errorValidation.$invalid
        },
        hasWarning() {
            return this.warningValidation && this.warningValidation.$invalid
        },
        headingNodes() {
            return getHeadingNodes(this.itemEditable.content[this.fieldSchema.name])
        },
    },
    methods: {
        scrollToField() {
            scrollItemTo({
                $elem: $(`.ItemContentFormFieldElement[fieldName=${this.fieldSchema.name}]`),
                adjustEditionPanel: true,
                adjustCurrentScroll: true,
            })
        },
        scrollToHeading(headingIndex) {
            // The prosemirror view concerned by the scroll
            let editor = this.tiptapEditors[this.fieldSchema.name]
            let headingPos

            // Find the node corresponding to the chosen heading
            editor.state.doc.descendants((node, offset) => {
                if (node.type.name == "heading") {
                    if (headingIndex == 0) {
                        headingPos = offset
                    }
                    headingIndex--
                }
            })

            // Not found, weird, bail out
            if (!headingPos) return

            // Get the coords of thie heading node, relative to the current scroll position
            let headingCoords = editor.view.coordsAtPos(headingPos)
            // Scroll to the coordinates of the heading,
            // adjusted for the top bar, the current scroll, and the sticky menu bar
            scrollItemTo({
                topCoord: headingCoords.top,
                offset: 40, // For the sticky menubar
                adjustEditionPanel: true,
                adjustCurrentScroll: true,
            })
        },
    },
}
</script>
