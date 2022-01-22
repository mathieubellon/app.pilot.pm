import $ from "jquery"
const DiffMatchPatch = require("diff-match-patch")
const JSONSortify = require("json.sortify")
import { Node } from "prosemirror-model"
import { ReplaceStep } from "prosemirror-transform"
import { Mapping } from "prosemirror-transform"

import { itemContentSchema } from "@richText/schema"

const BLOCK_NODE_START = "\u0011"
const BLOCK_NODE_END = "\u0012"
const NODE_LEAF = "\u0013"
const reWhitespace = /\s/

const DELTA_REMOVED = -1
const DELTA_ADDED = 1
const DELTA_UNCHANGED = 0

const DIFF_TIMEOUT = 5

/**
 * The main Differ object, with our custom timeout
 */
let diffMatchPatch = new DiffMatchPatch()
diffMatchPatch.Diff_Timeout = DIFF_TIMEOUT

const CUT_MODE_WORD = "word"
const CUT_MODE_CHAR = "char"

/***********************
 * Marked Strings & Node Meta Data
 ************************/

/**
 * A NodeMetaData represent the meta data at one position in a prosemirror document
 * It's may apply to either :
 *  - A textual character
 * Or
 *  - A node boundary ( START/END for block nodes or LEAF)
 *
 * The metadata that qualify this position are : marks, attrs, nodeType, parentNodes.
 *
 * We create and store an identity string, which is a built from those 4 metadata.
 * It it used to make a fast equality check between two nodes
 * (instead of a costly deep equals of the 4 metadata objects)
 */
class NodeMetaData {
    constructor(node, parentNodes, parentNodesAttrs) {
        let marks = node.marks.map((n) => n.toJSON()).sort()

        // No need to store marks & attrs for now,
        // keep them commented to reduce memory footprint

        // List of serialized marks on the character
        //this.marks = marks
        // Dict of attributes values on the character
        //this.attrs = node.attrs

        // A string representing the hierarchy of parent node above this character
        this.parentNodesString = parentNodes.join(">")
        // nodeType object from prosemirror
        this.nodeType = node.type

        // An identity string that fasten NodeMetaData comparison
        this.identity =
            this.nodeType.name +
            JSONSortify(marks) +
            JSONSortify(node.attrs) +
            this.parentNodesString +
            JSONSortify(parentNodesAttrs)
    }

    /**
     * Compare two NodeMetaData for equality,
     * Using their identity field
     */
    equals(nodeMetaData) {
        // Fail fast if trying to compare junk
        if (!(nodeMetaData instanceof NodeMetaData)) {
            return false
        }
        return this.identity == nodeMetaData.identity
    }

    /**
     * True if this a paragraph node boundary
     */
    isParagraphNode() {
        return this.nodeType.name == "paragraph"
    }

    /**
     * True if this a list node boundary
     */
    isListNode() {
        return this.nodeType.name == "bullet_list" || this.nodeType.name == "ordered_list"
    }

    /**
     * True if this a list node boundary
     */
    isHardBreak() {
        return this.nodeType.name == "hard_break"
    }

    /**
     * True if this is top-level Node
     */
    isTopLevelNode() {
        return this.parentNodesString == "doc"
    }
}

/**
 * An helper that create a String instance with context attributes attached to it :
 *  - startPos is the position of this string chunk into the prosemirror document
 *  - nodeMetaDataList is a reference to the whole NodeMetaData for the prosemirror document
 *
 *  An ideal solution would be a MarkedString subclass of String,
 *  but this isn't well supported by babel right now
 */
function createMarkedString(text, startPos, nodeMetaDataList) {
    let markedString = new String(text)
    markedString.startPos = startPos
    markedString.nodeMetaDataList = nodeMetaDataList
    return markedString
}

/**
 * An helper that retrieve the NodeMetaData of a character inside a markedString
 */
function getMetaData(markedString, index = 0) {
    return markedString.nodeMetaDataList[markedString.startPos + index]
}

/**
 * Compare two markedString for equality,
 * comparing each of their respective character
 * and NodeMetaData for equality.
 */
function markedStringEquals(left, right) {
    // The text must be the same
    if (left.valueOf() != right.valueOf()) return false

    // And the node meta data should also be the same, for each char
    for (let i = 0; i < left.length; i++) {
        if (!getMetaData(left, i).equals(getMetaData(right, i))) {
            return false
        }
    }
    return true
}

/**
 * An helper to create a markedString that is a substring of another markedString
 */
function sliceMarkedString(markedString, startIndex, endIndex) {
    return createMarkedString(
        markedString.slice(startIndex, endIndex),
        markedString.startPos + startIndex,
        markedString.nodeMetaDataList,
    )
}

/***********************
 * Prosemirror Node to MarkedString
 ************************/

/**
 * A function for generating serial unique id on Nodes
 */
{
    let id = 0
    Node.prototype.uniqueId = function () {
        if (typeof this.__uniqueid == "undefined") {
            this.__uniqueid = ++id
        }
        return this.__uniqueid
    }
}

/**
 * Transform a prosemirror document into a MarkedString.
 * The closing and opening node for the "doc" nodeType are not included in the returned sequence.
 *
 * This used to be a recursive function, but were translated to an iterative one for performances
 *
 * Example :
 *
 * {"type":"doc","content":[{"type":"paragraph","content":[{"type":"text","text": "you me" }]}]}
 * ==>
 * "\u0011you me\u0012" + nodeMetaDataList attribute on the MarkedString
 */
function docToMarkedString(doc) {
    // The result
    let markedString = ""
    let nodeMetaDataList = []
    // Maintains a list of parent nodes
    let parentNodes = ["doc"]
    let parentNodesAttrs = []
    // The next nodes to handle
    // They are stored in a reverse order ( the next node is the last element of the array, not the first )
    // because push()/pop() are muuuuch faster than shift()/unshift()
    let nextNodes = doc.content.content.slice().reverse()
    let blockNodesToClose = []

    let node, nodeId, nodeMarks, nodeMetaData, i

    function createNodeMetaData() {
        return new NodeMetaData(node, parentNodes, parentNodesAttrs)
    }

    while (nextNodes.length) {
        node = nextNodes.pop()
        nodeId = node.uniqueId()
        // Serialize the marks object into a plain object
        nodeMarks = node.marks.map((n) => n.toJSON())

        // For text nodes, each character in the node is converted to a MarkedCharacter instance
        if (node.type.name == "text") {
            markedString += node.text
            nodeMetaData = createNodeMetaData()
            for (i = 0; i < node.text.length; i++) {
                nodeMetaDataList.push(nodeMetaData)
            }
            // Go to the next node
            continue
        }

        // Leaf node are converted to a single MarkedCharacter
        if (node.type.isLeaf) {
            markedString += NODE_LEAF
            nodeMetaDataList.push(createNodeMetaData())
            // Go to the next node
            continue
        }

        // Deal with non-leaf block nodes

        if (!node.type.isBlock) {
            throw Error("Node should be a block type")
        }

        // Never seen block node : open it
        if (!blockNodesToClose[nodeId]) {
            // Mark the start of a block node
            nodeMetaData = createNodeMetaData()
            nodeMetaDataList.push(nodeMetaData)
            markedString += BLOCK_NODE_START

            parentNodes.push(node.type.name)
            parentNodesAttrs.push(node.attrs)
            nextNodes.push(node)

            // Handle child nodes before closing this block node
            if (node.content.size) {
                nextNodes.push(...node.content.content.slice().reverse())
            }

            blockNodesToClose[nodeId] = nodeMetaData
        }
        // Already seen node : close it
        else {
            parentNodes.pop()
            parentNodesAttrs.pop()

            // Mark the end of a block node
            markedString += BLOCK_NODE_END

            nodeMetaData = blockNodesToClose[nodeId]
            nodeMetaDataList.push(nodeMetaData)
        }
    }

    return createMarkedString(markedString, 0, nodeMetaDataList)
}

/***********************
 * Diffing between two MarkedString
 ************************/

function isAddedDelta(delta) {
    return delta[0] == DELTA_ADDED
}
function isRemovedDelta(delta) {
    return delta[0] == DELTA_REMOVED
}

/**
 * A friendly interface for diffing two marked strings.
 *
 * Hide the gory internals that are here for performances :
 *  - tokenization
 *  - encoding to a single-char unicode
 *  - bookkeeping of the tokenArray and tokenMap
 *  - actually diffing the encoded chars
 *  - Rehydrate the chars to markedString
 */
class MarkedStringDiff {
    constructor(leftMarkedString, rightMarkedString, cleanupSemantic, cutMode = CUT_MODE_WORD) {
        this.leftMarkedString = leftMarkedString
        this.rightMarkedString = rightMarkedString
        this.cutMode = cutMode

        this.tokenArray = [] // e.g. tokenArray[4] == 'Hello\n'
        this.tokenMap = {} // e.g. tokenMap['Hello\n'] == 4
        // '\x00' is a valid character, but various debuggers don't like it.
        // So we'll insert a junk entry to avoid generating a null character.
        this.tokenArray[0] = ""
        // Keeping our own length variable is faster than looking it up.
        this.tokenArrayLength = this.tokenArray.length

        // Tokenize and encode at the same time
        this.encodedLeftMarkedString = this.tokenizeAndEncodeMarkedString(this.leftMarkedString)
        this.encodedRightMarkedString = this.tokenizeAndEncodeMarkedString(this.rightMarkedString)

        // Apply the diff algorithm, and store the resulting deltaList
        this.deltaList = diffMatchPatch.diff_main(
            this.encodedLeftMarkedString,
            this.encodedRightMarkedString,
        )

        if (cleanupSemantic) {
            diffMatchPatch.diff_cleanupSemantic(this.deltaList)
        }

        // Rehydrate the encoded character into the initial marked string
        this.decodeCharsToMarkedString()
    }

    getTokenHash(token, startPos, nodeMetaDataList) {
        return token
            .split("")
            .map((char, i) => char + nodeMetaDataList[startPos + i].identity)
            .join("")
    }

    /**
     * Reduce a markedString token to an unique encoding Unicode character
     */
    encodeTokenToChar(token, startPos, nodeMetaDataList) {
        let tokenHash = this.getTokenHash(token, startPos, nodeMetaDataList)

        if (
            this.tokenMap.hasOwnProperty
                ? this.tokenMap.hasOwnProperty(tokenHash)
                : this.tokenMap[tokenHash] !== undefined
        ) {
            return String.fromCharCode(this.tokenMap[tokenHash])
        } else {
            this.tokenMap[tokenHash] = this.tokenArrayLength
            this.tokenArray[this.tokenArrayLength] = token
            return String.fromCharCode(this.tokenArrayLength++)
        }
    }

    tokenizeAndEncodeMarkedString(markedString) {
        if (this.cutMode == CUT_MODE_WORD)
            return this.tokenizeAndEncodeMarkedStringCutWord(markedString)
        else return this.tokenizeAndEncodeMarkedStringCutChar(markedString)
    }

    tokenizeAndEncodeMarkedStringCutChar(markedString) {
        return markedString
            .split("")
            .map((char, i) => this.encodeTokenToChar(char, i, markedString.nodeMetaDataList))
            .join("")
    }

    /**
     * The diff work on a MarkedString (produced by the docToMarkedString function )
     * We want to tokenize words : cut the string after whitespaces or block node end, to obtain a sequence of words.
     * We also include the block node boundaries into the starting and ending words
     *
     * Example :
     * "\u0011you me\u0012\u0011him\u0012"
     * ==>
     * [ "\u0011you ", "me\u0012", "\u0011him\u0012"]
     *
     */
    tokenizeAndEncodeMarkedStringCutWord(markedString) {
        let self = this
        let tokenizedWords = []
        let wordPosStart = 0
        let wordString = ""
        let markedChar

        function pushWord(pos) {
            if (!wordString) {
                return
            }
            let encodedWord = self.encodeTokenToChar(
                wordString,
                wordPosStart,
                markedString.nodeMetaDataList,
            )
            tokenizedWords.push(encodedWord)
            wordPosStart = pos + 1
        }

        function pushToken(markedChar, pos) {
            wordString += markedChar
            pushWord(pos)
            wordString = ""
        }

        function pushSingleCharToken(markedChar, pos) {
            pushWord(pos - 1)
            wordString = markedChar
            pushWord(pos)
            wordString = ""
        }

        for (let i = 0; i < markedString.length; i++) {
            markedChar = markedString[i]

            // Cut on whitespaces, except near end of node
            // ( in which case the next iteration will do the cut on BLOCK_NODE_END )
            if (reWhitespace.test(markedChar) && markedString[i + 1] != BLOCK_NODE_END) {
                pushToken(markedChar, i)
            }
            // Cut before opening/closing list nodes (ul and ol)
            // Then make a single-char word with the list node.
            // This is absolutely critical for a proper handling of list item diffing,
            // because it coordinate the strings from left and right on those nodes.
            else if (markedString.nodeMetaDataList[i].isListNode()) {
                pushSingleCharToken(markedChar, i)
            }
            // Cut before leaf nodes
            // Then add a single-char word with the leaf node.
            // With a special case for hard break that should be kept together with their preceding word
            // as for BLOCK_NODE_END characters.
            else if (markedChar == NODE_LEAF) {
                if (getMetaData(markedString, i).isHardBreak()) {
                    pushToken(markedChar, i)
                } else {
                    pushSingleCharToken(markedChar, i)
                }
            }
            // Node or non-whitespace textual characters
            else {
                // Block Node End
                if (
                    wordString.length &&
                    wordString[wordString.length - 1] == BLOCK_NODE_END &&
                    markedChar != BLOCK_NODE_END
                ) {
                    pushWord(i - 1)
                    wordString = ""
                }

                wordString += markedChar
            }
        }
        if (wordString.length) pushWord(markedString.length - 1)

        return tokenizedWords.join("")
    }

    /**
     * Rehydrate the text in a diff from a string of token hashes to real markedString
     */
    decodeCharsToMarkedString() {
        let startPosLeft = 0,
            startPosRight = 0
        let leftNodeMetaDataList = this.leftMarkedString.nodeMetaDataList,
            rightNodeMetaDataList = this.rightMarkedString.nodeMetaDataList

        for (let delta of this.deltaList) {
            let chars = delta[1]
            let added = isAddedDelta(delta),
                removed = isRemovedDelta(delta)
            let tokens = []

            for (let y = 0; y < chars.length; y++) {
                tokens[y] = this.tokenArray[chars.charCodeAt(y)]
            }

            let text = tokens.join("")

            delta[1] = createMarkedString(
                text,
                removed ? startPosLeft : startPosRight,
                removed ? leftNodeMetaDataList : rightNodeMetaDataList,
            )

            if (added) startPosRight += text.length
            else if (removed) startPosLeft += text.length
            else {
                startPosRight += text.length
                startPosLeft += text.length
            }
        }
    }
}

/**
 * Make a diff between two markedString.
 * Return a list of delta, using the diff-match-patch format,
 * but with markedString instead of normal strings.
 */
function diffMarkedString(
    leftMarkedString,
    rightMarkedString,
    cleanupSemantic,
    cutMode = CUT_MODE_WORD,
) {
    return new MarkedStringDiff(leftMarkedString, rightMarkedString, cleanupSemantic, cutMode)
        .deltaList
}

/***********************
 * DocDiff : Change List between two docs
 ************************/

/**
 * A Change represent a high-level modification that we'll expose to the user
 * It store a prosemirror step to reproduce the change on the original document
 * If there's an insertion, it will store the prosemirror slice added
 * If there's a deletion, it will store the prosemirror slice deleted
 */
class Change {
    constructor(step, sliceAdded, sliceRemoved) {
        this.step = step
        this.sliceAdded = sliceAdded
        this.sliceRemoved = sliceRemoved

        this.cachedAddedHtmlString = null
        this.cachedRemovedHtmlString = null

        this.addedBlockLength = 0
        this.removedBlockLength = 0

        if (sliceAdded) {
            this.addedBlockLength = sliceAdded.content.content.filter(
                (node) => node.type.isBlock,
            ).length
        }
        if (sliceRemoved) {
            this.removedBlockLength = sliceRemoved.content.content.filter(
                (node) => node.type.isBlock,
            ).length
        }
        this.isBLock = Boolean(this.addedBlockLength || this.removedBlockLength)
        this.id = "changeid-" + Math.floor(Math.random() * 0xffffffff)

        // For diff/merge views, track which change has been accepted or rejected
        this.accepted = true
    }

    /**
     * Compare two Change for equality,
     * comparing the slice added and slice removed
     */
    equals(change) {
        if (!(change instanceof Change)) return false

        return (
            this.sliceAdded.content.eq(change.sliceAdded.content) &&
            this.sliceRemoved.content.eq(change.sliceRemoved.content)
        )
    }

    getAddedDOMFragment() {
        if (!this.sliceAdded || this.sliceAdded.content.size == 0) return null
        return itemContentSchema.DOMSerializer.serializeFragment(this.sliceAdded.content)
    }
    getAddedHtmlString() {
        if (this.cachedAddedHtmlString === null) {
            let fragment = this.getAddedDOMFragment()
            this.cachedAddedHtmlString = fragment ? $("<div>").append(fragment).html() : ""
        }
        return this.cachedAddedHtmlString
    }

    getRemovedDOMFragment() {
        if (!this.sliceRemoved || this.sliceRemoved.content.size == 0) return null
        return itemContentSchema.DOMSerializer.serializeFragment(this.sliceRemoved.content)
    }
    getRemovedHtmlString() {
        if (this.cachedRemovedHtmlString === null) {
            let fragment = this.getRemovedDOMFragment()
            this.cachedRemovedHtmlString = fragment ? $("<div>").append(fragment).html() : ""
        }
        return this.cachedRemovedHtmlString
    }

    getAddedText() {
        return this.sliceAdded
            ? this.sliceAdded.content.textBetween(0, this.sliceAdded.content.size, " ").trim()
            : null
    }
    getDeletedText() {
        return this.sliceRemoved
            ? this.sliceRemoved.content.textBetween(0, this.sliceRemoved.content.size, " ").trim()
            : null
    }
}

/**
 * Entry-point for diffing two prosemirror doc.
 * This is what external code should use.
 */
class DocDiff {
    constructor(initialDoc, changedDoc, { isInverted = false, cutMode = CUT_MODE_WORD } = {}) {
        // The initial prosemirror document (left side of the diff)
        this.initialDoc = initialDoc
        // The modified prosemirror document (right side of the diff)
        this.changedDoc = changedDoc
        // If the initial&changed doc are inverted, and ins/del order of blocks should be swapped
        this.isInverted = isInverted
        // Default mode is to cut on word, which is less-precise but human-readable.
        // We can also cut on each char for a more precise diff
        this.cutMode = cutMode
        // The list of Change objects to apply this diff
        this.changes = []

        // MarkedString for the initial document
        this.initialMarkedString = docToMarkedString(initialDoc)
        // MarkedString for the modified document
        this.changedMarkedString = docToMarkedString(changedDoc)

        this.deltaList = diffMarkedString(
            this.initialMarkedString,
            this.changedMarkedString,
            false,
            this.cutMode,
        )

        // Init the list of Change from the diff deltaList
        if (this.deltaList) {
            this.initChangesFromDelta()
        }
    }

    /**
     *  Create a list of high-level Change from the low-level deltaList output from diff-match-patch
     */
    initChangesFromDelta() {
        this.posDelta = 0

        for (let i = 0; i < this.deltaList.length; i++) {
            let delta = this.deltaList[i]
            let addedMarkedString, removedMarkedString

            // An untouched part of the sequence
            if (delta[0] == DELTA_UNCHANGED) {
                continue
            }

            // Look for a "replacement", which is represented by two consecutive insertion + deletion
            // Combine the insertion and deletion into a single change
            if (isAddedDelta(delta)) {
                addedMarkedString = delta[1]
                if (this.deltaList[i + 1] && isRemovedDelta(this.deltaList[i + 1])) {
                    removedMarkedString = this.deltaList[++i][1]
                }
            }
            if (isRemovedDelta(delta)) {
                removedMarkedString = delta[1]
                if (this.deltaList[i + 1] && isAddedDelta(this.deltaList[i + 1])) {
                    addedMarkedString = this.deltaList[++i][1]
                }
            }

            this.createChange(addedMarkedString, removedMarkedString)

            // this.splitMarkedStringsAndCreateChanges(addedMarkedString, removedMarkedString)
        }
    }

    splitMarkedStringsAndCreateChanges(addedMarkedString, removedMarkedString) {
        // Split the sequences on each paragraphs
        let addedBlocks = this.splitTopLevelNodes(addedMarkedString),
            removedBlocks = this.splitTopLevelNodes(removedMarkedString)

        // Special case : when there's an empty doc in either side of the diff,
        // we must not let two separate changes, because that would lead
        // to a "remove change" on an empty doc (without empty paragraph),
        // which is an erroneous state.
        // We merge the two modification into one single change,
        // and trim the block modification so the change is inline.
        if (
            (this.initialDoc.nodeSize == 4 || this.changedDoc.nodeSize == 4) &&
            addedBlocks.length > 0 &&
            removedBlocks.length > 0
        ) {
            ;[addedBlocks[0], removedBlocks[0]] = this.trimIdenticalNodeCharacters(
                addedBlocks[0],
                removedBlocks[0],
            )
        }

        // Extract the head and tail blocks, that may be inlined (without their node markers)
        let {
            headInlineInsertion,
            headInlineDeletion,
            tailInlineInsertion,
            tailInlineDeletion,
        } = this.extractInlineBlocks(addedBlocks, removedBlocks)

        // Now that we have coherent blocks, we can create the changes

        // 1: Create a Change for the first insertion/deletion, if they are inline
        if (headInlineInsertion || headInlineDeletion)
            this.createChange(headInlineInsertion, headInlineDeletion)

        // 2: Create one Change for each intermediate insertion or deletion of a complete block
        // For normal diff, begin by the deletion so the user see them first
        // For inverted diff, begin by the insertion
        if (this.isInverted) {
            for (let addedBlock of addedBlocks) this.createChange(addedBlock, null)
        }
        for (let removedBlock of removedBlocks) this.createChange(null, removedBlock)
        if (!this.isInverted) {
            for (let addedBlock of addedBlocks) this.createChange(addedBlock, null)
        }

        // 3: Create a Change for the last insertion/deletion, if they are not a complete block
        if (tailInlineInsertion || tailInlineDeletion)
            this.createChange(tailInlineInsertion, tailInlineDeletion)
    }

    /**
     * Split a single MarkedString into a list of multiple MarkedString
     * where each new sequence represents content contained in a single outer paragraph Node
     *
     * The algorithm is simply to separate on each START paragraph node boundary
     */
    splitTopLevelNodes(markedString) {
        if (!markedString) {
            return []
        }

        let blockList = []

        let startPos = markedString.startPos
        let blockPosStart = startPos
        let blockString = ""

        function pushBlock(pos) {
            let markedBlock = createMarkedString(
                blockString,
                blockPosStart,
                markedString.nodeMetaDataList,
            )
            blockList.push(markedBlock)
            blockPosStart = startPos + pos + 1
        }

        let markedChar, nodeMetaData, i
        for (i = 0; i < markedString.length; i++) {
            markedChar = markedString[i]
            nodeMetaData = getMetaData(markedString, i)

            if (
                blockString.length &&
                markedChar == BLOCK_NODE_START &&
                //nodeMetaData.isParagraphNode()
                nodeMetaData.isTopLevelNode()
            ) {
                pushBlock(i - 1)
                blockString = ""
            }

            blockString += markedChar
        }
        if (blockString.length) {
            pushBlock(markedString.length - 1)
        }

        return blockList
    }

    /**
     * Given the added and removed blocks, try to extract the blocks at the head and tail
     * into inline blocks.
     * Inline blocks will have their identical node marker removed from their closing edge,
     * and their identical textual content removed from their opening edge.
     * This allow to display only the minimal different content into the diff.
     *
     * Inline blocks are removed from the addedBlocks and removedBlocks list.
     *
     * Up to 4 blocks may be affected :
     *  - head insertion
     *  - head deletion
     *  - tail insertion
     *  - tail deletion
     *
     * This function use the following algorithm:
     * 1/ pop the non-complete blocks from the list
     * 2/ strip the closing node markers from the two head blocks, only if they are strictly identical
     * 3/ strip the opening node markers from the two tail blocks, only if they are strictly identical
     * 4/ strip the identical starting textual content from the two head blocks
     * 5/ strip the identical ending textual content from the two tail blocks
     */
    extractInlineBlocks(addedBlocks, removedBlocks) {
        let headInlineInsertion = null,
            headInlineDeletion = null,
            tailInlineInsertion = null,
            tailInlineDeletion = null

        // Extract inline content (strings which are not a complete block)
        if (addedBlocks.length > 0 && !this.isCompleteBlock(addedBlocks[0]))
            headInlineInsertion = addedBlocks.shift()
        if (addedBlocks.length > 0 && !this.isCompleteBlock(addedBlocks[addedBlocks.length - 1]))
            tailInlineInsertion = addedBlocks.pop()
        if (removedBlocks.length > 0 && !this.isCompleteBlock(removedBlocks[0]))
            headInlineDeletion = removedBlocks.shift()
        if (
            removedBlocks.length > 0 &&
            !this.isCompleteBlock(removedBlocks[removedBlocks.length - 1])
        )
            tailInlineDeletion = removedBlocks.pop()

        // When we add blocks, this may push the head to the tail, swap them
        // Should we do the same when in non inverted mode ?
        if (this.isInverted && headInlineInsertion && !tailInlineInsertion && tailInlineDeletion) {
            tailInlineInsertion = headInlineInsertion
            headInlineInsertion = null
        }
        if (this.isInverted && headInlineDeletion && !tailInlineDeletion && tailInlineInsertion) {
            tailInlineDeletion = headInlineDeletion
            headInlineDeletion = null
        }

        // If the two head inline modification (ins/del) have a strictly identical node opening/closing,
        // then we can safely remove those node from the Change object.
        // If the node aren't equal, we keep them to show the structure modification to the user,
        // and the merge review feature needs them to keep a consistent structure.
        if (headInlineInsertion && headInlineDeletion) {
            ;[headInlineInsertion, headInlineDeletion] = this.trimIdenticalNodeCharacters(
                headInlineInsertion,
                headInlineDeletion,
            )
        }
        // Same for the tail
        if (tailInlineInsertion && tailInlineDeletion) {
            ;[tailInlineInsertion, tailInlineDeletion] = this.trimIdenticalNodeCharacters(
                tailInlineInsertion,
                tailInlineDeletion,
            )
        }

        // Remove identical content at the edge of the head/tail inline nodes
        // When the node structure is modified (for example, when moving hard break/paragraph around)
        // There's a glitch on the edge of the diff, where text would appear incorrectly modified.
        // That's because the diff tokens glue together the last word and the closing node char.
        // If only the closing node changes, then the last word appears incorrectly modified.
        // This detection prevent this incorrect behaviour.

        function canCut(markedChar) {
            return true

            //return /\W/.test(markedChar)

            /*return reWhitespace.test(markedChar)
                    || markedChar == NODE_LEAF
                    || markedChar == BLOCK_NODE_END
                    || markedChar == BLOCK_NODE_START*/
        }
        function trimIdenticalSides(left, right) {
            let sliceStart = 0,
                sliceEnd = 0,
                headOffset = 0,
                tailOffset = 0

            while (
                headOffset < left.length &&
                headOffset < right.length &&
                left[headOffset] == right[headOffset] &&
                getMetaData(left, headOffset).equals(getMetaData(right, headOffset))
            ) {
                headOffset++
                if (canCut(left[headOffset])) {
                    sliceStart = headOffset
                } else {
                    break
                }
            }

            while (
                tailOffset < left.length &&
                tailOffset < right.length &&
                left[left.length - tailOffset - 1] == right[right.length - tailOffset - 1] &&
                getMetaData(left, left.length - tailOffset - 1).equals(
                    getMetaData(right, right.length - tailOffset - 1),
                )
            ) {
                tailOffset++
                if (canCut(left[left.length - tailOffset - 1])) {
                    sliceEnd = tailOffset
                } else {
                    break
                }
            }

            if (sliceStart > 0 || sliceEnd > 0) {
                left = sliceMarkedString(left, sliceStart, left.length - sliceEnd)
                right = sliceMarkedString(right, sliceStart, right.length - sliceEnd)
            }
            return [left, right]
        }

        if (headInlineInsertion && headInlineDeletion) {
            ;[headInlineInsertion, headInlineDeletion] = trimIdenticalSides(
                headInlineInsertion,
                headInlineDeletion,
            )
        }
        // Same for the tail
        if (tailInlineInsertion && tailInlineDeletion) {
            ;[tailInlineInsertion, tailInlineDeletion] = trimIdenticalSides(
                tailInlineInsertion,
                tailInlineDeletion,
            )
        }

        return { headInlineInsertion, headInlineDeletion, tailInlineInsertion, tailInlineDeletion }
    }

    /**
     * Remove the opening/closing node characters, if they are identical on both string.
     * Block node and hard-break leaf node are affected.
     * The start and end of the string is processed separately,
     * the opening and closing do not need to correspond.
     * Ex :
     * <blockquote><p><span>left</span></p> | <blockquote><p>right</p>
     * ==>
     * <span>left</span> | right
     */
    trimIdenticalNodeCharacters(left, right) {
        let headOffset = 0
        let tailOffset = 0

        while (
            headOffset < left.length &&
            headOffset < right.length &&
            left[headOffset] == right[headOffset] &&
            getMetaData(left, headOffset).nodeType.name ==
                getMetaData(right, headOffset).nodeType.name &&
            (left[headOffset] == BLOCK_NODE_START || getMetaData(left, headOffset).isHardBreak())
        ) {
            headOffset++
        }
        while (
            tailOffset < left.length &&
            tailOffset < right.length &&
            left[left.length - tailOffset - 1] == right[right.length - tailOffset - 1] &&
            getMetaData(left, left.length - tailOffset - 1).nodeType.name ==
                getMetaData(right, right.length - tailOffset - 1).nodeType.name &&
            (left[left.length - tailOffset - 1] == BLOCK_NODE_END ||
                getMetaData(left, left.length - tailOffset - 1).isHardBreak())
        ) {
            tailOffset++
        }
        if (headOffset > 0 || tailOffset > 0) {
            tailOffset = tailOffset > 0 ? -tailOffset : undefined
            left = sliceMarkedString(left, headOffset, tailOffset)
            right = sliceMarkedString(right, headOffset, tailOffset)
        }

        return [left, right]
    }

    /**
     * A markedString is a considered a complete block if there's
     * a NODE_START char at the head and NODE_END char at the tail.
     */
    isCompleteBlock(markedString) {
        return (
            markedString[0] == BLOCK_NODE_START &&
            markedString[markedString.length - 1] == BLOCK_NODE_END &&
            getMetaData(markedString, 0).nodeType.name ==
                getMetaData(markedString, markedString.length - 1).nodeType.name
        )
    }

    /**
     * Create a change object and add it to the Change list
     * addedString and removedString are both MarkedString objects
     * One of them can be null, for insertion-only or deletion-only
     */
    createChange(addedString, removedString) {
        if (!addedString && !removedString) {
            return
        }

        // Handle the case where the node structure were modified on one edge, but not the text
        // This can happen for example when adding a paragraph at the edge of a blockquote
        if (addedString && removedString && markedStringEquals(addedString, removedString)) {
            return
        }

        let startPosAdded = null,
            endPosAdded = null,
            startPosRemoved = null,
            endPosRemoved = null

        if (addedString && addedString.length) {
            // Start pos is before the first char
            startPosAdded = addedString.startPos
            // End pos is after the last char
            endPosAdded = addedString.startPos + addedString.length
        }
        if (removedString && removedString.length) {
            // Start pos is before the first char
            startPosRemoved = removedString.startPos
            // End pos is after the last char
            endPosRemoved = removedString.startPos + removedString.length
        }

        // Case with only a deletion
        if (startPosAdded === null) startPosAdded = endPosAdded = startPosRemoved
        // Case with only an insertion
        // Use the position delta as an offset, to insert the content at the correct position
        if (startPosRemoved === null)
            startPosRemoved = endPosRemoved = startPosAdded - this.posDelta

        // Update the position delta
        this.posDelta += endPosAdded - startPosAdded - (endPosRemoved - startPosRemoved)

        // Now we can generate the Change object
        let sliceAdded = this.changedDoc.slice(startPosAdded, endPosAdded)
        let sliceRemoved = this.initialDoc.slice(startPosRemoved, endPosRemoved)

        // Prosemirror step to apply on the initial document if we want to transform it
        let step = new ReplaceStep(startPosRemoved, endPosRemoved, sliceAdded)

        let change = new Change(step, sliceAdded, sliceRemoved)
        this.changes.push(change)
    }

    /**
     * Get the position mapping associated needed to go from
     * the initial doc to the modified doc
     */
    getMapping() {
        let mapping = new Mapping()
        for (let change of this.changes) {
            mapping.appendMap(change.step.getMap())
        }
        return mapping
    }
}

export { DocDiff, Change }
