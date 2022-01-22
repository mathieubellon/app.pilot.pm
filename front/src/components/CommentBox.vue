<template>
<div class="CommentBox">
    <RichTextEditor
        class="border-transparent bg-white"
        :editor="editor"
        :excludeMenuBarItems="['heading', 'undo', 'redo', 'options']"
        @click="onClick"
    />

    <div
        v-show="isMentionDropdownVisible"
        class="CommentBox__mentionsDropdown shadow bg-white"
        ref="mentionsDropdown"
    >
        <div class="CommentBox__mentionsContent p-5">
            <div v-if="loadingMentions">
                {{ $t("loading") }}
            </div>

            <template v-else>
                <!-- 1/ Teams -->
                <div
                    v-for="mention in filteredTeamMentions"
                    class="CommentBox__mentionsResult"
                    :class="{ highlighted: isHighlighted(mention) }"
                    :key="mention.value"
                    @click="selectMention(mention)"
                >
                    <span
                        v-html="'@' + mention.highlighted"
                        class="truncate"
                    />
                    <span class="CommentBox__mentionCategory bg-purple-200">{{ $t("team") }}</span>
                </div>

                <!-- 2/ Groups -->
                <div
                    v-for="groupMention in groupMentions"
                    class="CommentBox__mentionsResult"
                    :class="{
                        highlighted: isHighlighted(groupMention),
                        inactive: inactiveMentionGroups[groupMention.id],
                    }"
                    :key="groupMention.value"
                    @click="selectMention(groupMention)"
                >
                    <span v-html="'@' + groupMention.value" />
                    <span class="CommentBox__mentionCategory bg-indigo-200">
                        {{ contentType.name }}
                    </span>
                </div>

                <!-- 3/ Users -->
                <div
                    v-for="mention in filteredUserMentions"
                    class="CommentBox__mentionsResult"
                    :class="{ highlighted: isHighlighted(mention) }"
                    :key="mention.value"
                    @click="selectMention(mention)"
                >
                    <span class="flex truncate">
                        <UserAvatar
                            size="20px"
                            :user="mention.user"
                        />
                        <span
                            v-html="'@' + mention.highlighted"
                            class="truncate"
                        />
                    </span>
                    <span class="CommentBox__mentionCategory bg-teal-100">{{ $t("user") }}</span>
                </div>

                <!-- 4/ @all -->
                <div
                    class="CommentBox__mentionsResult"
                    :class="{
                        highlighted: isHighlighted(allUsersMention),
                        confirm: allUserMentionSelected,
                    }"
                    @click="selectMention(allUsersMention)"
                >
                    <template v-if="allUserMentionSelected">
                        {{ $t("selectAgainToConfirmAllUsers") }}
                    </template>
                    <template v-else>
                        @{{ allUsersMention.value }}
                        <span class="CommentBox__mentionCategory bg-orange-300">
                            {{ $t("everybodyOnDesk") }}
                        </span>
                    </template>
                </div>
            </template>
        </div>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import $ from "jquery"
import { mapState, mapGetters, mapMutations, mapActions } from "vuex"
import { initialDataPromise } from "@js/bootstrap"
import fuzzysort from "fuzzysort"
import Popper from "popper.js"
import PopperUtils from "popper.js/dist/esm/popper-utils.js"
import { Editor, Extension } from "tiptap"
import browser from "prosemirror-view/src/browser"
import { removeEmptyParagraphsFromSlice } from "@richText/cleaning"
import { EMPTY_PROSEMIRROR_DOC, commentSchema } from "@richText/schema"
import { keyCodes, isSpace } from "@js/utils"
import BoxEscapingWatcher from "@js/BoxEscapingWatcher"
import PilotMixin from "@components/PilotMixin"

import RichTextEditor from "@richText/RichTextEditor"

let CHAR_WIDTH = 10 // Approximate pixel width of a character

const MENTION_GROUPS = {
    all: {
        en: "all",
        fr: "tous",
    },
    owners: {
        en: "owners",
        fr: "responsables",
    },
    members: {
        en: "members",
        fr: "membres",
    },
    channelOwners: {
        en: "channelOwners",
        fr: "responsablesCanaux",
    },
}

export default {
    name: "CommentBox",
    mixins: [PilotMixin],
    components: {
        RichTextEditor,
    },
    props: {
        value: null,
        autoFocus: Boolean,

        contentType: Object,
        // Tell which group to deactivate because they have no users inside them
        inactiveMentionGroups: {
            type: Object,
            default: () => ({}),
        },
    },
    data: () => ({
        editor: null,

        allUserMentions: [],
        allTeamMentions: [],

        filteredUserMentions: [],
        filteredTeamMentions: [],
        // A Promise initialized in the created() hook
        fetchMentionsPromise: null,
        loadingMentions: false,
        allUserMentionSelected: false,

        hideMentionDropdown: false,
        highlightedMentionIndex: 0,
        isNavigatingDropown: false,
        // A flag that track when a mention has just been selected,
        // to prevent the onFocus handler to re-open the mention dropdown
        mentionHasBeenSelected: false,
        // A flag that track when we're walking through the document to mark unmarked mentions
        isMarking: false,

        caretPosition: null,
        caretCoordinates: null,
    }),
    computed: {
        ...mapState("choices", ["choices"]),
        ...mapState("usersAdmin", ["teams"]),

        /***********************
         * Groups
         ************************/
        allUsersMention() {
            let locale = window.pilot.currentLocale
            return {
                value: MENTION_GROUPS.all[locale],
                entity: "group",
                id: "all",
            }
        },

        groupMentions() {
            if (!this.contentType) {
                return []
            }

            // No group on the wiki pages
            if (this.contentType.id == window.pilot.contentTypes.WikiPage.id) {
                return []
            }

            let locale = window.pilot.currentLocale
            let groupNames = ["owners", "members", "channelOwners"]
            // No members on the items
            if (this.contentType.id == window.pilot.contentTypes.Item.id) {
                groupNames = ["owners", "channelOwners"]
            }
            return groupNames.map((groupName) => ({
                value: MENTION_GROUPS[groupName][locale],
                entity: "group",
                id: groupName,
            }))
        },

        /***********************
         * Dropdown helpers
         ************************/
        isMentionDropdownVisible() {
            return this.mentionSearch && !this.hideMentionDropdown
        },

        activeGroupMentions() {
            return this.groupMentions.filter(
                (groupMention) => !this.inactiveMentionGroups[groupMention.name],
            )
        },

        mentionList() {
            return [
                ...this.filteredTeamMentions,
                ...this.activeGroupMentions,
                ...this.filteredUserMentions,
                this.allUsersMention,
            ]
        },

        highlightedMention() {
            return this.mentionList[this.highlightedMentionIndex]
        },

        mentionsByName() {
            let allMentions = [
                ...this.allTeamMentions,
                ...this.activeGroupMentions,
                ...this.allUserMentions,
                this.allUsersMention,
            ]
            return _.keyBy(allMentions, "value")
        },

        /***********************
         * Mention search string calculation
         ************************/

        mentionStartPos() {
            let endPos = this.caretPosition,
                startPos = endPos - 1
            while (startPos >= 1) {
                let char = this.charAt(startPos)
                if (!char || isSpace(char)) {
                    return null
                }

                let previousChar = this.charAt(startPos - 1)
                if (char == "@" && (!previousChar || isSpace(previousChar))) {
                    return startPos
                }

                startPos--
            }
            return null
        },

        mentionEndPos() {
            if (this.mentionStartPos === null) {
                return null
            }

            let endPos = this.mentionStartPos
            while (this.charAt(endPos) && !isSpace(this.charAt(endPos))) {
                endPos++
            }
            return endPos
        },

        mentionSearch() {
            if (this.mentionStartPos === null || this.mentionEndPos === null) {
                return null
            }
            return this.editor.state.doc.textBetween(this.mentionStartPos, this.mentionEndPos)
        },
    },
    watch: {
        value(newValue) {
            if (!_.isEqual(newValue, this.editor.getJSON())) {
                this.editor.setContent(newValue)
            }
        },

        caretPosition() {
            this.computeAvailableMentions()
        },

        isMentionDropdownVisible() {
            if (this.isMentionDropdownVisible === true) {
                this.mentionsEscapingWatcher.startWatching()
            } else if (this.isMentionDropdownVisible === false) {
                this.mentionsEscapingWatcher.stopWatching()
            }
        },
    },
    methods: {
        charAt(pos) {
            // (nodeSize -2) because the last position is for node closing, no text there,
            // and we'll do the text between pos and (pos+1)
            if (pos < 0 || pos >= this.editor.state.doc.nodeSize - 2) {
                return null
            }
            return this.editor.state.doc.textBetween(pos, pos + 1)
        },

        updateValue() {
            // If the input has been generated by the markUnmarkedMentions, don't update the value again
            if (this.isMarking) {
                return
            }

            this.markUnmarkedMentions()
            this.$emit("input", this.editor.getJSON())
        },

        updateCaretPosition() {
            // Trigger the mention search only when the selection is at a single character,
            // and not a range selection
            if (this.editor.selection.from != this.editor.selection.to) {
                this.caretPosition = null
            } else {
                this.caretPosition = this.editor.selection.from
            }

            // The caret position computation is expensive (especially on IE11 which sucks at DOM manipulation).
            // Do it only when necessary, if the dropdown is visible
            if (this.isMentionDropdownVisible) {
                this.caretCoordinates = this.editor.view.coordsAtPos(this.caretPosition)
                this.popperJS.scheduleUpdate()
            }
        },

        getMentionPopperPositionRect() {
            if (this.caretCoordinates && this.editor) {
                return {
                    top: this.caretCoordinates.top,
                    right: this.caretCoordinates.left + CHAR_WIDTH,
                    bottom: this.caretCoordinates.bottom,
                    left: this.caretCoordinates.left,
                    width: CHAR_WIDTH, // Approximate width of a character
                    height: this.caretCoordinates.top - this.caretCoordinates.bottom,
                }
            } else {
                return { top: 0, right: 0, bottom: 0, left: 0, width: 0, height: 0 }
            }
        },

        /***********************
         * Mention selection
         ************************/

        computeAvailableMentions() {
            this.filteredUserMentions = []
            this.filteredTeamMentions = []
            if (!this.mentionSearch || !this.fetchMentionsPromise) {
                return
            }

            this.loadingMentions = true
            // Wait for the teams and users choices to be available
            this.fetchMentionsPromise.then(() => {
                this.loadingMentions = false

                if (this.mentionSearch == "@") {
                    this.filteredUserMentions = this.allUserMentions
                    this.filteredTeamMentions = this.allTeamMentions
                    return
                }

                let mentionSearch = this.mentionSearch.slice(1)

                let userMatches = fuzzysort.go(mentionSearch, this.choices.users, {
                    key: "fuzzyPrepared",
                })
                let teamMatches = fuzzysort.go(mentionSearch, this.teams, {
                    key: "fuzzyPrepared",
                })

                this.filteredUserMentions = userMatches.map((result) => ({
                    value: result.target,
                    highlighted: fuzzysort.highlight(result),
                    user: result.obj,
                    entity: "user",
                    id: result.obj.id,
                }))
                this.filteredTeamMentions = teamMatches.map((result) => ({
                    value: result.target,
                    highlighted: fuzzysort.highlight(result),
                    team: result.obj,
                    entity: "team",
                    id: result.obj.id,
                }))

                // Pre-select the best match
                if (this.filteredTeamMentions.length > 0) {
                    this.resetDropdownNavigation(0)
                } else if (this.filteredUserMentions.length > 0) {
                    this.resetDropdownNavigation(
                        this.filteredTeamMentions.length + this.activeGroupMentions.length,
                    )
                }
            })
        },

        insertMention(mention, from, to) {
            let maybeSpace = isSpace(this.charAt(to + 1)) ? "" : " "
            this.editor.dispatchTransaction(
                this.editor.state.tr.insertText(mention.value + maybeSpace, from + 1, to).addMark(
                    from,
                    from + mention.value.length + 1,
                    this.editor.schema.mark("mention", {
                        entity: mention.entity,
                        id: mention.id,
                        uid: `mention-${mention.entity}-${mention.id}`,
                    }),
                ),
            )
        },

        selectMention(mention) {
            if (mention.entity == "group" && this.inactiveMentionGroups[mention.id]) {
                return
            }

            if (mention.id == "all" && !this.allUserMentionSelected) {
                this.allUserMentionSelected = true
                return
            }

            this.insertMention(mention, this.mentionStartPos, this.mentionEndPos)

            // Hide the dropdown
            this.hideMentionDropdown = true
            this.resetDropdownNavigation()
            // We generally want to show the mention dropdown when we gain focus.
            // Except when we just clicked on the mention dropdown to select one,
            // in which case we want to keep it hidden.
            this.mentionHasBeenSelected = true
            // After 1/2 second, we can show again the mention dropdown on focus
            setTimeout(() => (this.mentionHasBeenSelected = false), 500)

            this.editor.focus()
        },

        markUnmarkedMentions() {
            if (!this.editor) {
                return
            }

            this.isMarking = true

            this.editor.state.doc.descendants((node, pos, parent) => {
                // Returns if the node already has a mention mark, or there is no text
                if (this.editor.schema.marks.mention.isInSet(node.marks) || !node.text) {
                    return
                }

                for (let i = 0; i < node.text.length; i++) {
                    if (node.text[i] === "@") {
                        let start = i
                        let end = start
                        while (node.text[end] && !isSpace(node.text[end])) {
                            end++
                        }
                        i = end
                        let mentionName = node.textBetween(start + 1, end)
                        let mention = this.mentionsByName[mentionName]
                        if (mention) {
                            this.insertMention(mention, pos + start, pos + end + 1)
                        }
                    }
                }
            })

            this.isMarking = false
        },

        /***********************
         * Keyboard navigation
         ************************/
        isHighlighted(mention) {
            // There's an hardcore bug on IE11 where the textArea lose focus
            // when Vue.js add or remove the "highlighted" :class on mentionResult elements.
            // We could not find a correct fix, so we just deactivate the highlighting on IE11.
            if (browser.ie) return false
            return mention == this.highlightedMention
        },
        resetDropdownNavigation(index = -1) {
            this.highlightedMentionIndex = index
            this.isNavigatingDropown = false
            this.allUserMentionSelected = false
        },
        moveUp() {
            this.isNavigatingDropown = true
            if (this.highlightedMentionIndex > 0) this.highlightedMentionIndex--
        },
        moveDown() {
            this.isNavigatingDropown = true
            if (this.highlightedMentionIndex < this.mentionList.length - 1)
                this.highlightedMentionIndex++
        },
        onKeydown(editorView, event) {
            let key = event.which || event.keyCode
            switch (key) {
                /**
                 * Navigating into the dropdown
                 */
                case keyCodes.ARROW_UP:
                    if (this.isMentionDropdownVisible) {
                        this.moveUp()
                        return true
                    }
                    break
                case keyCodes.ARROW_DOWN:
                    if (this.isMentionDropdownVisible) {
                        this.moveDown()
                        return true
                    }
                    break

                /**
                 * Select into the dropdown
                 */
                case keyCodes.ENTER:
                    if (this.isMentionDropdownVisible && this.highlightedMention) {
                        this.selectMention(this.highlightedMention)
                        return true
                    }
                    break
                case keyCodes.ESCAPE:
                    if (this.isMentionDropdownVisible) {
                        // Hide the dropdown until a non-navigation key happen
                        this.hideMentionDropdown = true
                        return true
                    }
                    break
                case keyCodes.TAB:
                    if (this.isMentionDropdownVisible && this.highlightedMention) {
                        this.selectMention(this.highlightedMention)
                        return true
                    }
                    break
                default:
                    // If we're not navigating, the dropdown can be seen again
                    this.hideMentionDropdown = false
                    // On any non-navigation key, we reset the indicies to prevent overflow
                    this.resetDropdownNavigation()
                    break
            }
        },

        /***********************
         * Other events
         ************************/

        onEditorTransaction() {
            this.updateCaretPosition()
        },
        onClick() {
            // After a click, the dropdown can be seen again
            this.hideMentionDropdown = false
            // The click reset the navigation
            this.resetDropdownNavigation()
            this.$emit("click")
        },
        onFocus() {
            // We generally want to show the mention dropdown when we gain focus.
            // Except when we just clicked on the mention dropdown to select one,
            // in which case we want to keep it hidden.
            if (this.mentionHasBeenSelected) {
                return
            }

            // After a focus, the dropdown can be seen again
            this.hideMentionDropdown = false
            // The focus reset the navigation
            this.resetDropdownNavigation()
        },

        /***********************
         * Event setup / tearDown
         ************************/

        onScrollOrResize() {
            this.updateCaretPosition()
        },

        attachEventHandlers() {
            // Update popper on scroll and window resize
            this.scrollParent = $(PopperUtils.getScrollParent(this.$el))
            this.scrollParent.on("scroll", this.onScrollOrResize)
            $(window).on("resize", this.onScrollOrResize)

            // Close the mention dropdown when clicking outside it
            this.mentionsEscapingWatcher = new BoxEscapingWatcher(
                () => [this.$el, this.$refs.mentionsDropdown],
                () => {
                    this.hideMentionDropdown = true
                },
            )
        },

        detachEventHandlers() {
            this.scrollParent.off("scroll", this.onScrollOrResize)
            $(window).off("resize", this.onScrollOrResize)
            this.mentionsEscapingWatcher.stopWatching()
        },
    },
    created() {
        // Fetch the choices for mentions
        this.fetchMentionsPromise = new Promise((resolve, reject) => {
            initialDataPromise
                .then(() => {
                    for (let user of this.choices.users) {
                        if (!user.fuzzyPrepared) {
                            user.fuzzyPrepared = fuzzysort.prepare(user.username)
                        }

                        this.allUserMentions.push({
                            value: user.username,
                            highlighted: user.username,
                            user: user,
                            entity: "user",
                            id: user.id,
                        })
                    }
                    for (let team of this.teams) {
                        if (!team.fuzzyPrepared) {
                            team.fuzzyPrepared = fuzzysort.prepare(team.name)
                        }

                        this.allTeamMentions.push({
                            value: team.name,
                            highlighted: team.name,
                            team: team,
                            entity: "team",
                            id: team.id,
                        })
                    }

                    resolve()
                })
                .catch((error) => reject(error))
        })

        // Init the Editor
        let value = this.value
        if (_.isEmpty(value)) {
            value = EMPTY_PROSEMIRROR_DOC
        }

        // Tiptap defines a default keymap for the 'Enter' key,
        // which triggers before the onKeydown callback has a chance to handle it.
        // We need to define our own keymap to take precedence over the one defined by tiptap.
        let handleEnterExtension = new Extension()
        handleEnterExtension.keys = () => ({
            Enter: () => {
                if (this.isMentionDropdownVisible && this.highlightedMention) {
                    this.selectMention(this.highlightedMention)
                    return true
                }
            },
        })

        this.editor = new Editor({
            content: value,
            extensions: [handleEnterExtension, ...commentSchema.getExtensions()],
            onUpdate: this.updateValue,
            onTransaction: this.onEditorTransaction,
            onFocus: this.onFocus,
            serializer: commentSchema.DOMSerializer,
            autoFocus: this.autoFocus,
            editorProps: {
                placeholder: this.$t("addComment"),
                handleKeyDown: this.onKeydown,
                handleClick: this.onClick,
                transformPasted: removeEmptyParagraphsFromSlice,
            },
            injectCSS: false,
        })
        // Convert value prop entered as HTML into a proper prosemirror doc
        if (_.isString(this.value)) {
            this.$emit("input", this.editor.getJSON())
        }
    },
    mounted() {
        // Move the popper to the end of the app to make positioning easier
        $(this.$refs.mentionsDropdown).appendTo("body")

        // Setup the popperJs where the dropdown will show up
        let popperReference = {
            getBoundingClientRect: () => this.getMentionPopperPositionRect(),
            clientWidth: CHAR_WIDTH,
            clientHeight: 0,
        }

        this.popperJS = new Popper(popperReference, this.$refs.mentionsDropdown, {
            placement: "bottom",
            modifiers: {
                flip: {
                    behavior: ["bottom", "top", "right", "left"],
                },
            },
        })

        this.attachEventHandlers()
    },
    beforeDestroy() {
        if (this.popperJS) {
            this.popperJS.destroy()
        }
        // Elements appended to body must be removed manually, because Vue.js won't do it automatically.
        if (this.$refs.mentionsDropdown) {
            this.$refs.mentionsDropdown.remove()
        }

        // Create a closure for setTimeout
        let editor = this.editor
        // Destroy after a timeout to show a nice disappearing transition
        setTimeout(() => {
            // Some browsers don't like that we destroy the editor after we removed the CommentBox from the DOM.
            // Just silence the error, this isn't important.
            try {
                editor.destroy()
            } catch (error) {}
        }, 500)
        this.detachEventHandlers()
    },
    i18n: {
        messages: {
            fr: {
                clickToSeeAllUsers: "ou affichez tous les utilisateurs",
                everybodyOnDesk: "Desk",
                helptext1: "Tapez quelques lettres pour filtrer la liste",
                selectAgainToConfirmAllUsers: "Sélectionner à nouveau pour confirmer @tous",
                team: "Equipe",
                user: "Utilisateur",
            },
            en: {
                clickToSeeAllUsers: "or see all users",
                everybodyOnDesk: "Desk",
                helptext1: "Continue to write to filter list",
                selectAgainToConfirmAllUsers: "Select again to confirm @all",
                team: "Team",
                user: "User",
            },
        },
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.CommentBox__mentionsDropdown {
    position: absolute;
    // Above Popper (100)
    z-index: 110;
    height: auto;
    max-height: 400px;
    width: 300px;
    overflow: auto;
    border-radius: 4px;
    border: solid $grey300 1px;
}

.CommentBox__mentionsContent {
    @apply flex flex-col flex-grow bg-white w-full p-4;
}

.CommentBox__mentionsResult {
    @apply flex items-center p-1 justify-between;
    cursor: pointer;

    b {
        @apply bg-yellow-300 text-blue-600;
        font-weight: normal;
    }
    &:hover,
    &.highlighted {
        background-color: $gray-lighter;
        border-radius: 4px;
        color: inherit;
    }
    &.inactive {
        color: $gray-light;
    }
    &.confirm {
        background-color: $yellow;
    }
}

.CommentBox__mentionCategory {
    @apply text-xs text-gray-600 px-2 rounded-lg;
}

.CommentBox__textarea {
    textarea {
        overflow: hidden;
    }
}
</style>
