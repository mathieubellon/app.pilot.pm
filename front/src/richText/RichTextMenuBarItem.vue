<template>
<button
    v-show="visibleMenuBarItems[name]"
    :class="buttonClass"
    :key="name"
    type="button"
    @click="onClick"
>
    <div
        v-if="showIcon"
        class="RichTextMenuBarItem__icon"
        :style="iconSizeStyle"
    >
        <component :is="icons[iconName ? iconName : name]" />
    </div>
    <span
        v-if="label"
        :class="{ 'ml-2': showIcon }"
    >
        {{ label }}
    </span>
</button>
</template>

<script>
/**
 * Icons copied from https://github.com/scrumpy/tiptap/blob/master/examples/Components/Icon/index.vue
 */
import annotate from "./icons/annotate.svg"
import blockquote from "./icons/blockquote.svg"
import bullet_list from "./icons/bullet_list.svg"
import code from "./icons/code.svg"
import code_block from "./icons/code.svg"
import em from "./icons/italic.svg"
import horizontal_rule from "./icons/horizontal_rule.svg"
import image from "./icons/image.svg"
import link from "./icons/link.svg"
import ordered_list from "./icons/ordered_list.svg"
import paragraph from "./icons/paragraph.svg"
import redo from "./icons/redo.svg"
import strike from "./icons/strike.svg"
import strong from "./icons/bold.svg"
import underline from "./icons/underline.svg"
import undo from "./icons/undo.svg"

// Table icons
import addColumnAfter from "./icons/add_col_after.svg"
import addColumnBefore from "./icons/add_col_before.svg"
import addRowAfter from "./icons/add_row_after.svg"
import addRowBefore from "./icons/add_row_before.svg"
import createTable from "./icons/table.svg"
import deleteColumn from "./icons/delete_col.svg"
import deleteRow from "./icons/delete_row.svg"
import deleteTable from "./icons/delete_table.svg"
import toggleCellMerge from "./icons/combine_cells.svg"

const ICONS = {
    annotate,
    blockquote,
    bullet_list,
    code,
    code_block,
    em,
    horizontal_rule,
    image,
    link,
    ordered_list,
    paragraph,
    redo,
    strike,
    strong,
    underline,
    undo,

    // Table icons
    addColumnAfter,
    addColumnBefore,
    addRowAfter,
    addRowBefore,
    createTable,
    deleteColumn,
    deleteRow,
    deleteTable,
    toggleCellMerge,
}

export default {
    name: "RichTextMenuBarItem",
    inject: ["editor", "visibleMenuBarItems"],
    props: {
        name: String,
        label: String,
        showIcon: {
            type: Boolean,
            default: true,
        },
        iconName: String,
        attrs: Object,
        disabled: {
            type: Boolean,
            default: false,
        },
        inDropdown: {
            type: Boolean,
            default: false,
        },
        bubbleClick: {
            type: Boolean,
            default: false,
        },
        iconSize: {
            type: String,
        },
    },
    data: () => ({
        icons: ICONS,
    }),
    computed: {
        buttonClass() {
            return {
                RichTextMenuBar__dropdownElement: this.inDropdown,
                RichTextMenuBar__button: !this.inDropdown,
                isActive: this.isActive,
                disabled: this.disabled,
            }
        },
        isActive() {
            return this.editor.isActive[this.name] && this.editor.isActive[this.name](this.attrs)
        },
        iconSizeStyle() {
            if (this.iconSize) {
                return {
                    width: this.iconSize,
                    height: this.iconSize,
                }
            }
            return {}
        },
    },
    methods: {
        onClick(event) {
            if (this.bubbleClick) {
                this.$emit("click", event)
            } else {
                this.editor.commands[this.name](this.attrs)
            }
        },
    },
}
</script>

<style lang="scss">
.RichTextMenuBarItem__icon {
    position: relative;
    display: inline-flex;
    vertical-align: middle;
    width: 0.75rem;
    height: 0.75rem;
    margin: 0 0.1rem;

    svg {
        display: inline-block;
        vertical-align: top;
        width: 100%;
        height: 100%;
        fill: currentColor;
        stroke: none;
    }
}
</style>
