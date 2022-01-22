<template>
<!--
The RichTextMenuBar component contains the menu items, and also the prompt & tooltips associated with some of those menu items ( image, link ).

The menubar must adapt gracefully to any width its contained into. The width may be constrained by the viewport or by the container element ( annotation box ).
The menu items may be located either in the main menu bar ( "inline" state ), or moved into a dropdown to save space ( "dropdown" state ). The dropdown is openable by an item at the end of the menubar.
The width of the menuBar is provided in this.witdh ( computed during the mounted() hook and recomputed in case of window resize ).
Each menu item that can be moved into the dropdown is declared in both the main menu bar and the dropdown, and its visibility is managed by two exclusive v-show.
The width breakpoints are defined in this.breakpoints, which depends on WIDTHS_BREAKPOINTS and the visibility of some menu items.
Nota : v-show is prefered over v-if, otherwise Vue has trouble keeping track of each menu item positions ( issues with component reuse ).

Example :

    <RichTextMenuBarItem name="ordered_list" v-show="width >= breakpoints.seventh" />

    <Popper
        <RichTextMenuBarItem name="ordered_list" v-show="width < breakpoints.seventh" />
    </Popper>


IMPORTANT NOTE : every <button> declared here MUST have a type="button" to prevent form submission
when the RichTextEditor is inserted into a form.
The <button> declared by <RichTextMenuBarItem> do it as well.
-->
<div class="RichTextMenuBar">
    <EditorMenuBar
        v-if="!readOnly"
        v-slot="{ isActive }"
        class="RichTextMenuBar_menuItems"
        :class="{ faded: isMenuBarFaded }"
        :editor="editor"
    >
        <!-- // TipTap lib apply a display:none; to this exact div beneath, do not style it, don not remove-->
        <div>
            <!-- ^^^DO NOT remove ^^^ -->
            <div class="flex flex-row items-center">
                <!---------------------->
                <!-- Heading Dropdown -->
                <!---------------------->
                <Popper
                    :appendToBody="true"
                    closeOnClickSelector="button"
                    placement="bottom"
                    triggerElementName="HeadingPopper"
                    triggerType="click"
                >
                    <template #triggerElement>
                        <button
                            v-show="visibleMenuBarItems.heading && width >= breakpoints.sixth"
                            class="RichTextMenuBar__button"
                            :class="{ isActive: isActive.heading() }"
                            ref="HeadingPopper"
                            type="button"
                        >
                            Aa
                            <!-- The empty span is required to correctly align with flex display -->
                            <span>
                                <Icon
                                    class="caret"
                                    name="ChevronDown"
                                />
                            </span>
                        </button>
                    </template>

                    <template #content>
                        <RichTextMenuBarHeadingMenu />
                    </template>
                </Popper>

                <span
                    v-show="visibleMenuBarItems.heading && width >= breakpoints.sixth"
                    class="RichTextMenuBar__separator"
                />

                <!---------------------->
                <!-- Marks -->
                <!---------------------->
                <RichTextMenuBarItem name="strong" />
                <RichTextMenuBarItem name="em" />

                <Popper
                    :appendToBody="true"
                    closeOnClickSelector="button"
                    placement="bottom"
                    triggerElementName="MarksPopper"
                    triggerType="click"
                >
                    <template #triggerElement>
                        <button
                            v-show="width >= breakpoints.first"
                            class="RichTextMenuBar__button"
                            :class="{
                                isActive:
                                    isActive.strike() || isActive.underline() || isActive.code(),
                            }"
                            ref="MarksPopper"
                            type="button"
                        >
                            <Icon name="MenuDotsHorizontal" />
                        </button>
                    </template>

                    <template #content>
                        <div class="flex flex-col">
                            <RichTextMenuBarItem
                                name="strike"
                                :inDropdown="true"
                                :label="$t('mark.strike')"
                            />
                            <RichTextMenuBarItem
                                name="underline"
                                :inDropdown="true"
                                :label="$t('mark.underline')"
                            />
                            <RichTextMenuBarItem
                                name="code"
                                :inDropdown="true"
                                :label="$t('mark.code')"
                            />
                        </div>
                    </template>
                </Popper>

                <span
                    v-show="width >= breakpoints.sixth"
                    class="RichTextMenuBar__separator"
                />

                <!---------------------->
                <!-- Nodes -->
                <!---------------------->
                <RichTextMenuBarItem name="bullet_list" />

                <RichTextMenuBarItem
                    v-show="width >= breakpoints.seventh"
                    name="ordered_list"
                />

                <RichTextMenuBarItem
                    v-show="withImage && width >= breakpoints.fifth"
                    name="image"
                    :bubbleClick="true"
                    @click="openImagePrompt()"
                />

                <Popper
                    :appendToBody="true"
                    closeOnClickSelector="button"
                    placement="bottom"
                    triggerElementName="NodePopper"
                    triggerType="click"
                >
                    <template #triggerElement>
                        <button
                            v-show="width >= breakpoints.first"
                            class="RichTextMenuBar__button"
                            :class="{
                                isActive:
                                    isActive.blockquote() ||
                                    isActive.code_block() ||
                                    isActive.horizontal_rule(),
                            }"
                            ref="NodePopper"
                            type="button"
                        >
                            <Icon name="MenuDotsHorizontal" />
                        </button>
                    </template>

                    <template #content>
                        <div class="flex flex-col">
                            <RichTextMenuBarItem
                                name="blockquote"
                                :inDropdown="true"
                                :label="$t('block.blockquote')"
                            />
                            <RichTextMenuBarItem
                                name="code_block"
                                iconName="code"
                                :inDropdown="true"
                                :label="$t('block.codeBlock')"
                            />
                            <RichTextMenuBarItem
                                name="horizontal_rule"
                                :inDropdown="true"
                                :label="$t('block.horizontalRule')"
                            />
                        </div>
                    </template>
                </Popper>

                <span
                    v-show="width >= breakpoints.sixth"
                    class="RichTextMenuBar__separator"
                />

                <!---------------------->
                <!-- Table -->
                <!---------------------->

                <template v-if="withTable && visibleMenuBarItems.createTable">
                    <Popper
                        :appendToBody="true"
                        closeOnClickSelector="button"
                        placement="bottom"
                        triggerElementName="TablePopper"
                        triggerType="click"
                    >
                        <template #triggerElement>
                            <button
                                v-show="width >= breakpoints.first"
                                class="RichTextMenuBar__button w-5 h-5"
                                key="TablePopper"
                                ref="TablePopper"
                                type="button"
                            >
                                <TableIcon />
                            </button>
                        </template>

                        <template #content>
                            <div class="flex flex-col">
                                <RichTextMenuBarTableItems />
                            </div>
                        </template>
                    </Popper>

                    <span
                        v-show="width >= breakpoints.first"
                        class="RichTextMenuBar__separator"
                    />
                </template>

                <!---------------------->
                <!-- Link, Annotations, Emoji -->
                <!---------------------->

                <RichTextMenuBarItem
                    name="link"
                    :bubbleClick="true"
                    :disabled="selection.empty"
                    @click="openLinkPrompt()"
                />

                <RichTextMenuBarItem
                    v-show="withAnnotations && width >= breakpoints.fourth"
                    name="annotate"
                    :bubbleClick="true"
                    :disabled="!canAnnotate"
                    iconSize="16px"
                    @click="onAnnotateClick"
                />

                <button
                    v-show="withMention"
                    class="RichTextMenuBar__button"
                    name="mention"
                    :disabled="!canMention"
                    type="button"
                    @click="onMentionClick"
                >
                    @
                </button>

                <Popper
                    ref="EmojiPopper"
                    :appendToBody="true"
                    placement="bottom"
                    triggerElementName="EmojiPopperReference"
                    triggerType="click"
                >
                    <template #triggerElement>
                        <button
                            class="RichTextMenuBar__button is-emoji"
                            ref="EmojiPopperReference"
                            type="button"
                        >
                            😊
                        </button>
                    </template>

                    <template #content>
                        <EmojiPicker
                            class="z-10"
                            :data="emojiIndex"
                            emoji="point_up"
                            :i18n="$t('emojiPicker')"
                            :native="true"
                            :title="$t('emojiPicker.selectEmoji')"
                            @select="onEmojiSelect"
                        />
                    </template>
                </Popper>

                <span
                    v-show="
                        (visibleMenuBarItems.undo || visibleMenuBarItems.redo) &&
                        width >= breakpoints.third
                    "
                    class="RichTextMenuBar__separator"
                />

                <!---------------------->
                <!-- History ( undo, redo ) -->
                <!---------------------->

                <RichTextMenuBarItem
                    v-show="visibleMenuBarItems.undo && width >= breakpoints.third"
                    name="undo"
                />
                <RichTextMenuBarItem
                    v-show="visibleMenuBarItems.redo && width >= breakpoints.third"
                    name="redo"
                />

                <span
                    v-show="visibleMenuBarItems.options && width >= breakpoints.second"
                    class="RichTextMenuBar__separator"
                />

                <!---------------------->
                <!-- Options -->
                <!---------------------->

                <Popper
                    :appendToBody="true"
                    closeOnClickSelector="button"
                    placement="bottom"
                    triggerElementName="OptionsPopper"
                    triggerType="click"
                >
                    <template #triggerElement>
                        <button
                            v-show="visibleMenuBarItems.options && width >= breakpoints.second"
                            class="RichTextMenuBar__button text-xs font-medium"
                            ref="OptionsPopper"
                            type="button"
                        >
                            {{ $t("options") }}
                        </button>
                    </template>

                    <template #content>
                        <RichTextMenuBarOptionsMenu :editor="editor" />
                    </template>
                </Popper>

                <span
                    v-show="width < breakpoints.first"
                    class="RichTextMenuBar__separator"
                />

                <!---------------------->
                <!-- "More items" dropdown for small widths -->
                <!---------------------->

                <Popper
                    :appendToBody="true"
                    closeOnClickSelector="button:not(.OptionsTrigger):not(.HeadingTrigger):not(.TableTrigger)"
                    placement="bottom"
                    triggerElementName="MoreItemsPopper"
                    triggerType="click"
                >
                    <template #triggerElement>
                        <button
                            v-show="width < breakpoints.first"
                            class="RichTextMenuBar__button"
                            ref="MoreItemsPopper"
                            type="button"
                        >
                            <Icon name="MenuDotsHorizontal" />
                        </button>
                    </template>

                    <template #content>
                        <div class="flex flex-col">
                            <!---------------------->
                            <!-- Heading Dropdown -->
                            <!---------------------->
                            <Popper
                                :appendToBody="true"
                                closeOnClickSelector="button"
                                placement="bottom"
                                triggerElementName="HeadingPopperInDropdown"
                                triggerType="click"
                            >
                                <template #triggerElement>
                                    <button
                                        v-show="
                                            visibleMenuBarItems.heading && width < breakpoints.sixth
                                        "
                                        class="RichTextMenuBar__dropdownElement HeadingTrigger"
                                        :class="{ isActive: isActive.heading() }"
                                        ref="HeadingPopperInDropdown"
                                        type="button"
                                    >
                                        Aa
                                        <span class="ml-2">{{ $t("block.heading") }}</span>
                                    </button>
                                </template>

                                <template #content>
                                    <RichTextMenuBarHeadingMenu />
                                </template>
                            </Popper>

                            <hr v-show="visibleMenuBarItems.heading && width < breakpoints.sixth" />

                            <!---------------------->
                            <!-- Marks -->
                            <!---------------------->

                            <RichTextMenuBarItem
                                v-show="width < breakpoints.first"
                                name="strike"
                                :inDropdown="true"
                                :label="$t('mark.strike')"
                            />
                            <RichTextMenuBarItem
                                v-show="width < breakpoints.first"
                                name="underline"
                                :inDropdown="true"
                                :label="$t('mark.underline')"
                            />
                            <RichTextMenuBarItem
                                v-show="width < breakpoints.first"
                                name="code"
                                :inDropdown="true"
                                :label="$t('mark.code')"
                            />

                            <hr />

                            <!---------------------->
                            <!-- Nodes -->
                            <!---------------------->

                            <RichTextMenuBarItem
                                v-show="width < breakpoints.seventh"
                                name="ordered_list"
                                :inDropdown="true"
                                :label="$t('block.orderedList')"
                            />

                            <RichTextMenuBarItem
                                v-show="withImage && width < breakpoints.fifth"
                                name="image"
                                :bubbleClick="true"
                                :inDropdown="true"
                                :label="$t('block.image')"
                                @click="openImagePrompt()"
                            />

                            <RichTextMenuBarItem
                                v-show="width < breakpoints.first"
                                name="blockquote"
                                :inDropdown="true"
                                :label="$t('block.blockquote')"
                            />
                            <RichTextMenuBarItem
                                v-show="width < breakpoints.first"
                                name="code_block"
                                iconName="code"
                                :inDropdown="true"
                                :label="$t('block.codeBlock')"
                            />
                            <RichTextMenuBarItem
                                v-show="width < breakpoints.first"
                                name="horizontal_rule"
                                :inDropdown="true"
                                :label="$t('block.horizontalRule')"
                            />

                            <hr
                                v-show="
                                    width < breakpoints.first &&
                                    (withAnnotations ||
                                        visibleMenuBarItems.undo ||
                                        visibleMenuBarItems.redo ||
                                        visibleMenuBarItems.options)
                                "
                            />

                            <!---------------------->
                            <!-- Table popper -->
                            <!---------------------->

                            <Popper
                                :appendToBody="true"
                                closeOnClickSelector="button"
                                placement="bottom"
                                triggerElementName="TablePopperInDropdown"
                                triggerType="click"
                            >
                                <template #triggerElement>
                                    <button
                                        v-show="
                                            visibleMenuBarItems.createTable &&
                                            withTable &&
                                            width < breakpoints.first
                                        "
                                        class="RichTextMenuBar__dropdownElement TableTrigger"
                                        ref="TablePopperInDropdown"
                                        type="button"
                                    >
                                        <div class="RichTextMenuBarItem__icon mr-2">
                                            <TableIcon />
                                        </div>
                                        {{ $t("others.table") }}
                                    </button>
                                </template>

                                <template #content>
                                    <RichTextMenuBarTableItems />
                                </template>
                            </Popper>

                            <hr
                                v-show="
                                    visibleMenuBarItems.createTable &&
                                    withTable &&
                                    width < breakpoints.second
                                "
                            />

                            <!---------------------->
                            <!-- Annotations, History -->
                            <!---------------------->

                            <RichTextMenuBarItem
                                v-show="withAnnotations && width < breakpoints.fourth"
                                name="annotate"
                                :bubbleClick="true"
                                :disabled="!canAnnotate"
                                iconSize="16px"
                                :inDropdown="true"
                                :label="$t('others.annotate')"
                                @click="onAnnotateClick"
                            />

                            <RichTextMenuBarItem
                                v-show="visibleMenuBarItems.undo && width < breakpoints.third"
                                name="undo"
                                :inDropdown="true"
                                :label="$t('history.undo')"
                            />

                            <RichTextMenuBarItem
                                v-show="visibleMenuBarItems.redo && width < breakpoints.third"
                                name="redo"
                                :inDropdown="true"
                                :label="$t('history.redo')"
                            />

                            <!---------------------->
                            <!-- Options -->
                            <!---------------------->

                            <Popper
                                :appendToBody="true"
                                closeOnClickSelector="button"
                                placement="bottom"
                                triggerElementName="OptionsPopperInDropdown"
                                triggerType="click"
                            >
                                <template #triggerElement>
                                    <button
                                        v-show="
                                            visibleMenuBarItems.options &&
                                            width < breakpoints.second
                                        "
                                        class="RichTextMenuBar__dropdownElement OptionsTrigger"
                                        ref="OptionsPopperInDropdown"
                                        type="button"
                                    >
                                        {{ $t("options") }}
                                    </button>
                                </template>

                                <template #content>
                                    <RichTextMenuBarOptionsMenu :editor="editor" />
                                </template>
                            </Popper>
                        </div>
                    </template>
                </Popper>
            </div>
        </div>
    </EditorMenuBar>

    <!-- IMAGE PROMPT -->
    <RichTextImagePrompt
        v-if="withImage"
        :imageAttrs="imageAttrs"
        @submit="createOrEditImage"
    />

    <!-- IMAGE TOOLTIP -->
    <RichTextTooltip
        v-if="withImage"
        ref="imageTooltip"
        :positionBoundingRect="positionBoundingRect"
        :show="isImageTooltipVisible"
        @escape="closeImageTooltip"
    >
        <div class="RichTextMenuBar__imageTooltip">
            <a @click="setImageAlignment('left')">
                {{ $t("left") }}
            </a>
            <a @click="setImageAlignment('center')">
                {{ $t("center") }}
            </a>
            <a @click="setImageAlignment('right')">
                {{ $t("right") }}
            </a>
            |
            <a @click="openImagePrompt">
                {{ $t("edit") }}
            </a>
            |
            <a @click="removeImage">
                {{ $t("delete") }}
            </a>
        </div>
    </RichTextTooltip>

    <!-- LINK PROMPT -->
    <RichTextLinkPrompt
        :linkAttrs="linkAttrs"
        @submit="createOrEditLink"
    />

    <!-- LINK TOOLTIP -->
    <RichTextTooltip
        ref="linkTooltip"
        :positionBoundingRect="positionBoundingRect"
        :show="isLinkTooltipVisible"
        @escape="closeLinkTooltip"
    >
        <div class="RichTextMenuBar__linkTooltip">
            <a
                :href="linkAttrs.href"
                rel="noreferrer noopener nofollow"
                target="_blank"
                :title="linkAttrs.title"
            >
                {{ linkAttrs.href }}
            </a>
            <template v-if="!readOnly">
                |
                <a @click="openLinkPrompt">
                    {{ $t("edit") }}
                </a>
                |
                <a @click="removeLink">
                    {{ $t("delete") }}
                </a>
            </template>
        </div>
    </RichTextTooltip>
</div>
</template>

<script>
import _ from "lodash"
import $ from "jquery"
import { EditorMenuBar, Plugin as ProsemirrorPlugin } from "tiptap"
import { getMarkAttrs } from "tiptap-utils"
import {
    getSelectionBoundingRect,
    getNodeSelectionBoundingRect,
    getEmptyBoundingBox,
    isImageSelected,
    getSelectedImageNode,
    linkAroundSelection,
} from "@/richText/utils"
import { getRandomId, isSpace } from "@js/utils"

import data from "emoji-mart-vue-fast/data/all.json"
import { Picker as EmojiPicker, EmojiIndex } from "emoji-mart-vue-fast"

import Popper from "@components/Popper.vue"
import Icon from "@components/Icon.vue"
import RichTextMenuBarItem from "./RichTextMenuBarItem"
import RichTextMenuBarHeadingMenu from "./RichTextMenuBarHeadingMenu"
import RichTextMenuBarOptionsMenu from "./RichTextMenuBarOptionsMenu"
import RichTextMenuBarTableItems from "./RichTextMenuBarTableItems"
import RichTextLinkPrompt from "./RichTextLinkPrompt"
import RichTextImagePrompt from "./RichTextImagePrompt"
import RichTextTooltip from "./RichTextTooltip"
import TableIcon from "./icons/table.svg"

const emojiIndex = new EmojiIndex(data)

const WIDTHS_BREAKPOINTS = {
    first: 575,
    second: 505,
    third: 445,
    fourth: 380,
    fifth: 340,
    sixth: 320,
    seventh: 250,
}

const ALL_MENU_BAR_ITEMS_VISIBLE = {
    paragraph: true,
    heading: true,
    strong: true,
    em: true,
    strike: true,
    underline: true,
    code: true,
    bullet_list: true,
    ordered_list: true,
    blockquote: true,
    code_block: true,
    horizontal_rule: true,
    image: true,
    link: true,
    annotate: true,
    mention: true,
    emoji: true,
    undo: true,
    redo: true,
    options: true,

    // Table items
    addColumnAfter: true,
    addColumnBefore: true,
    addRowAfter: true,
    addRowBefore: true,
    createTable: true,
    deleteColumn: true,
    deleteRow: true,
    deleteTable: true,
    toggleCellMerge: true,
}

export default {
    name: "RichTextMenuBar",
    components: {
        EditorMenuBar,
        EmojiPicker,
        Popper,
        Icon,
        RichTextMenuBarItem,
        RichTextMenuBarHeadingMenu,
        RichTextMenuBarOptionsMenu,
        RichTextMenuBarTableItems,
        RichTextLinkPrompt,
        RichTextImagePrompt,
        RichTextTooltip,
        TableIcon,
    },
    props: {
        editor: {
            type: Object,
            required: true,
        },
        annotationManager: Object,
        excludeMenuBarItems: Array,
        readOnly: {
            type: Boolean,
            default: false,
        },
        canFade: {
            type: Boolean,
            default: false,
        },
    },
    provide() {
        return {
            editor: this.editor,
            editorId: this.editorId,
            visibleMenuBarItems: this.visibleMenuBarItems,
            annotationManager: this.annotationManager,
        }
    },
    data: () => ({
        width: 0,
        visibleMenuBarItems: {},

        editorId: getRandomId(),
        selection: {},
        positionBoundingRect: {},

        isLinkTooltipVisible: false,
        isImageTooltipVisible: false,

        // Track clicks that are not directly in the prosemirror editor,
        // but should keep the menubar open ( on the menubar, or inside the editor container )
        lastClickInEditor: false,

        imageAttrs: {
            src: "",
            caption: "",
            title: "",
            alt: "",
        },
        linkAttrs: {
            href: "",
            title: "",
        },

        emojiIndex,
    }),
    computed: {
        isMenuBarFaded() {
            return this.canFade && !(this.editor.focused || this.lastClickInEditor)
        },
        withAnnotations() {
            return Boolean(this.annotationManager)
        },
        withImage() {
            return this.editor.schema.nodes.image
        },
        withMention() {
            return this.editor.schema.marks.mention
        },
        withTable() {
            return this.editor.schema.nodes.table
        },
        /**
         * User can annotate only if a range is selected (selection is not empty),
         * and there's an annotation manager for this editor
         */
        canAnnotate() {
            return this.annotationManager && !this.selection.empty
        },
        /**
         * User can annotate only if the selection is empty ( no range is selected )
         */
        canMention() {
            return this.selection.empty
        },

        /**
         * The width breakpoints where some inline menu items should move to the dropdown.
         * The const WIDTHS_BREAKPOINTS suppose that all items are present.
         * This computed value will adapt those constants depending on the menu items present in this bar,
         * which depends on the editor schema and the visibleMenuBarItems prop.
         */
        breakpoints() {
            let adaptedBreakpoints = _.clone(WIDTHS_BREAKPOINTS)
            if (!this.withAnnotations || !this.visibleMenuBarItems.annotate) {
                adaptedBreakpoints.first -= 31
                adaptedBreakpoints.second -= 31
                adaptedBreakpoints.third -= 31
                adaptedBreakpoints.fourth -= 31
            }
            if (!this.withImage || !this.visibleMenuBarItems.image) {
                adaptedBreakpoints.first -= 27
                adaptedBreakpoints.second -= 27
                adaptedBreakpoints.third -= 27
            }
            if (!this.withMention || !this.visibleMenuBarItems.mention) {
                adaptedBreakpoints = _.mapValues(adaptedBreakpoints, (width) => width - 23)
            }
            if (!this.withTable || !this.visibleMenuBarItems.createTable) {
                adaptedBreakpoints = _.mapValues(adaptedBreakpoints, (width) => width - 30)
            }
            return adaptedBreakpoints
        },
    },
    methods: {
        update() {
            // No focus on the editor : don't do anything
            if (!this.editor.view.hasFocus()) {
                return
            }

            this.width = $(this.$el).width()

            this.isLinkTooltipVisible = false
            this.isImageTooltipVisible = false

            this.selection = this.editor.state.selection

            // Link tooltip
            if (this.selection.empty && this.editor.isActive.link()) {
                let attrs = getMarkAttrs(this.editor.state, this.editor.schema.marks.link)
                this.linkAttrs = _.clone(attrs)
                this.positionBoundingRect = this.getTooltipPosition()
                this.isLinkTooltipVisible = true
            }

            // No other menu/tooltip than the linkTooltip should be displayed when in readOnly
            else if (this.readOnly) {
                return
            }

            // Image tooltip
            if (isImageSelected(this.selection)) {
                let { imageNode, imagePos } = getSelectedImageNode(this.selection)
                this.imageAttrs = _.clone(imageNode.attrs)
                let domNode = this.editor.view.nodeDOM(imagePos)
                this.positionBoundingRect = domNode
                    ? domNode.getBoundingClientRect()
                    : this.getTooltipPosition()
                this.isImageTooltipVisible = true
            }
        },
        closeImageTooltip() {
            this.isImageTooltipVisible = false
        },
        closeLinkTooltip() {
            this.isLinkTooltipVisible = false
        },
        getTooltipPosition() {
            if (!this.editor || !this.editor.view) return getEmptyBoundingBox()

            let { empty, node } = this.selection

            if (node && node.type.isBlock) {
                // Block node selection
                return getNodeSelectionBoundingRect(this.editor)
            } else if (empty) {
                // Empty selection
                return getSelectionBoundingRect(this.editor)
            } else {
                // Node or text selection
                return node
                    ? getNodeSelectionBoundingRect(this.editor)
                    : getSelectionBoundingRect(this.editor)
            }
        },

        /***********************
         * Menu item actions that are not direct prosemirror commands
         ************************/
        setImageAlignment(alignment) {
            this.imageAttrs.alignment = alignment
            this.editor.commands.image(this.imageAttrs)
        },
        openImagePrompt() {
            let { imageNode } = getSelectedImageNode(this.selection)

            // Edition
            if (imageNode) {
                this.closeImageTooltip()
            }
            // Creation
            else {
                this.imageAttrs = {
                    src: "",
                    caption: "",
                    title: "",
                    alt: "",
                }
            }

            this.$modal.show(`imagePrompt-${this.editorId}`)
        },
        createOrEditImage() {
            this.editor.commands.image(this.imageAttrs)
            this.$modal.hide(`imagePrompt-${this.editorId}`)
        },
        removeImage() {
            let { imagePos } = getSelectedImageNode(this.selection)
            this.editor.dispatchTransaction(this.editor.state.tr.delete(imagePos, imagePos + 1))
            this.closeImageTooltip()
        },

        openLinkPrompt() {
            let { linkMark } = linkAroundSelection(this.editor)

            // Edition
            if (linkMark) {
                this.closeLinkTooltip()
            }
            // Creation
            else {
                if (this.selection.empty) {
                    return
                }

                this.linkAttrs = {
                    href: "",
                    title: "",
                }
            }

            this.$modal.show(`linkPrompt-${this.editorId}`)
        },
        createOrEditLink() {
            let { linkMark, startPos, endPos } = linkAroundSelection(this.editor)

            // Edition
            if (linkMark) {
                this.editor.dispatchTransaction(
                    this.editor.state.tr
                        .removeMark(startPos, endPos, linkMark)
                        .addMark(startPos, endPos, linkMark.type.create(this.linkAttrs)),
                )
            }
            // Creation
            else {
                // Ensure the url starts with http://
                if (!/^https?:\/\//i.test(this.linkAttrs.href)) {
                    this.linkAttrs.href = "http://" + this.linkAttrs.href
                }
                this.editor.commands.link(this.linkAttrs)
            }

            this.$modal.hide(`linkPrompt-${this.editorId}`)
        },
        removeLink() {
            let { linkMark, startPos, endPos } = linkAroundSelection(this.editor)
            this.editor.dispatchTransaction(
                this.editor.state.tr.removeMark(startPos, endPos, linkMark),
            )
            this.closeLinkTooltip()
        },

        onAnnotateClick() {
            if (this.canAnnotate) {
                this.annotationManager.startAnnotationCreation()
            }
        },

        onMentionClick() {
            if (this.canMention) {
                let previousChar = this.editor.state.doc.textBetween(
                    this.editor.selection.from - 1,
                    this.editor.selection.from,
                )
                let toInsert = isSpace(previousChar) ? "@" : " @"
                this.editor.dispatchTransaction(this.editor.state.tr.insertText(toInsert))
                this.editor.focus()
            }
        },

        onEmojiSelect(emoji) {
            this.$refs.EmojiPopper.hidePopper()
            this.editor.dispatchTransaction(this.editor.state.tr.insertText(emoji.native))
            this.editor.focus()
        },

        /**
         * Track clicks that are not directly in the prosemirror editor,
         * but should keep the menubar open ( on the menubar, or inside the editor container )
         */
        onDocumentClick(event) {
            let container = $(this.$el)
            if (container.closest(".ItemContentFormFieldElement").length) {
                container = container.closest(".ItemContentFormFieldElement")
            } else if (container.closest(".RichTextEditor").length) {
                container = container.closest(".RichTextEditor")
            } else if (container.closest(".CommentBox").length) {
                container = container.closest(".CommentBox")
            }
            this.lastClickInEditor = container[0].contains(event.target)
        },
    },
    created() {
        _.assign(this.visibleMenuBarItems, ALL_MENU_BAR_ITEMS_VISIBLE)
        for (let itemName of this.excludeMenuBarItems || []) {
            this.visibleMenuBarItems[itemName] = false
        }

        this.selection = this.editor.selection

        this.editor.registerPlugin(
            new ProsemirrorPlugin({
                view: () => ({
                    update: () => {
                        this.update()
                        if (this.$refs.linkTooltip && this.isLinkTooltipVisible)
                            this.$refs.linkTooltip.schedulePopperUpdate()
                        if (this.$refs.imageTooltip && this.isImageTooltipVisible)
                            this.$refs.imageTooltip.schedulePopperUpdate()
                    },
                }),
            }),
        )
        this.editor.on("focus", this.update)

        if (this.canFade) {
            $(document).on("click", this.onDocumentClick)
        }
    },
    mounted() {
        setTimeout(() => (this.width = $(this.$el).width()), 1)
        this.onWindowsResize = () => (this.width = $(this.$el).width())
        $(window).on("resize", this.onWindowsResize)
    },
    beforeDestroy() {
        if (this.canFade) {
            $(document).off("click", this.onDocumentClick)
        }
        if (this.onWindowsResize) {
            $(window).off("resize", this.onWindowsResize)
        }
    },
    i18n: {
        messages: {
            fr: {
                block: {
                    blockquote: "Citation",
                    codeBlock: "Bloc de code",
                    heading: "Titre",
                    horizontalRule: "Séparateur horizontal",
                    image: "Image",
                    orderedList: "Liste numérotée",
                    paragraph: "Texte normal",
                },
                emojiPicker: {
                    search: "Recherche",
                    selectEmoji: "Sélectionnez un emoji",
                    notfound: "Aucun emoji trouvé",
                    categories: {
                        search: "Résultats de la recherche",
                        recent: "Fréquemment utilisés",
                        smileys: "Smileys & Emotions",
                        people: "Personnes & Corps humain",
                        nature: "Animaux & Nature",
                        foods: "Aliments & Boissons",
                        activity: "Activités",
                        places: "Voyages & Lieux",
                        objects: "Objets",
                        symbols: "Symboles",
                        flags: "Drapeaux",
                        custom: "Personnalisés",
                    },
                },
                history: {
                    redo: "Rétablir",
                    undo: "Annuler",
                },
                mark: {
                    strike: "Barré",
                    underline: "Souligné",
                    code: "Code",
                },
                others: {
                    annotate: "Annoter",
                    table: "Table",
                },
            },
            en: {
                block: {
                    blockquote: "Quote",
                    codeBlock: "Code block",
                    heading: "Heading",
                    horizontalRule: "Horizontal separator",
                    image: "Image",
                    orderedList: "Ordered list",
                    paragraph: "Normal text",
                },
                emojiPicker: {
                    search: "Search",
                    selectEmoji: "Select emoji",
                    notfound: "No Emoji Found",
                    categories: {
                        search: "Search Results",
                        recent: "Frequently Used",
                        smileys: "Smileys & Emotion",
                        people: "People & Body",
                        nature: "Animals & Nature",
                        foods: "Food & Drink",
                        activity: "Activity",
                        places: "Travel & Places",
                        objects: "Objects",
                        symbols: "Symbols",
                        flags: "Flags",
                        custom: "Custom",
                    },
                },
                history: {
                    redo: "Redo",
                    undo: "Undo",
                },
                mark: {
                    strike: "Strike",
                    underline: "Underline",
                    code: "Code",
                },
                others: {
                    annotate: "Annotate",
                    table: "Table",
                },
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";
@import "~@sass/richText.scss";
@import "~@sass/dropdown.scss";
@import "~emoji-mart-vue-fast/css/emoji-mart.css";

.RichTextMenuBar {
    @apply sticky top-0 rounded-lg;
    z-index: 1;
}

/**
WARNING : The order between .RichTextMenuBar__button and .RichTextMenuBar_menuItems is important.
The faded text-color must take precedence over the disabled text-color,
so .RichTextMenuBar_menuItems must appears AFTER .RichTextMenuBar__button
**/
.RichTextMenuBar__button {
    line-height: 1.2rem;
    @apply flex items-center justify-center text-xs font-medium p-1 m-1;

    &.isActive {
        @apply bg-gray-300;
    }

    &:hover {
        @apply bg-gray-100;
    }

    &.disabled {
        cursor: default;

        &:hover {
            background: none;
        }

        svg {
            @apply text-gray-400;
        }
    }
}

.RichTextMenuBar_menuItems {
    @apply bg-white border-b border-gray-200;
    transition: opacity 0.2s, color 0.2s, border 0.2s, background-color 0.2s;

    /*
    &.faded{
        @apply bg-gray-50 text-gray-200 border-transparent shadow-none;
        opacity: .5;
        .RichTextMenuBar__button{
            @apply bg-gray-50;
        }
        .is-emoji {
            opacity: .2;
        }
        svg{
            @apply text-gray-200;
        }
    }
     */
}

.RichTextMenuBar__separator {
    display: inline-block;
    vertical-align: middle;
    width: 1px;
    height: 1.4rem;
    @apply bg-gray-200 flex-shrink-0;
    margin: 0 0.1rem;
}

.RichTextMenuBar .popper {
    min-width: 150px;
}

@mixin heading($size) {
    font-size: $size;
    line-height: $size;
}
button.RichTextMenuBar__dropdownElement {
    @apply p-2 text-left;

    &:hover {
        @apply bg-gray-100;
    }

    &.isActive {
        @apply bg-gray-300;
    }

    &.disabled {
        @apply text-gray-400 cursor-default;

        &:hover {
            background: none;
        }

        svg {
            @apply text-gray-400;
        }
    }

    &.heading1 {
        @include heading($h1);
    }
    &.heading2 {
        @include heading($h2);
    }
    &.heading3 {
        @include heading($h3);
    }
    &.heading4 {
        @include heading($h4);
    }
    &.heading5 {
        @include heading($h5);
    }
    &.heading6 {
        @include heading($h6);
    }
}

/* ==========================================================================
    Image/Link Tooltips
    ========================================================================== */

.RichTextMenuBar__imageTooltip,
.RichTextMenuBar__linkTooltip {
    display: flex;
    flex-wrap: nowrap;
    padding: 0.5em;

    a {
        margin: 0em 1em;
    }
}

/* ==========================================================================
Emoji
========================================================================== */

// We remove "Segoe UI Symbol" from the default emoji-mart font families,
// because it leads to an horrible emoji rendering on win7/FF
.emoji-type-native {
    font-family: "Segoe UI Emoji", "Segoe UI", "Apple Color Emoji", "Twemoji Mozilla",
        "Noto Color Emoji", "EmojiOne Color", "Android Emoji";
}
</style>
