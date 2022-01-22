import _ from "lodash"
import { EditorState, Plugin, PluginKey } from "prosemirror-state"
import { Step } from "prosemirror-transform"
import { EditorView } from "prosemirror-view"
import { Editor } from "tiptap"
import { Change } from "@js/diff/docDiff"
import { itemContentSchema } from "@richText/schema"
import { diffAndMergePlugin } from "@richText/extensions/diffAndMerge"
import { getRandomId } from "@js/utils"

const CHUNK_SIZE = 50
const BLOCKING_THRESHOLD = 250

class DiffRowEditor extends Editor {
    init(options = {}) {
        this.keymaps = []
        this.inputRules = []
        this.pasteRules = []
        this.commands = []
        this.nodes = []
        this.marks = []
        this.plugins = [diffAndMergePlugin]

        this.setOptions({
            ...this.defaultOptions,
            ...options,
        })
        this.focused = false
        this.selection = { from: 0, to: 0 }
        this.element = document.createElement("div")
        this.extensions = this.createExtensions()
        this.schema = itemContentSchema.prosemirrorSchema
        this.view = this.createView()

        // give extension manager access to our view
        this.extensions.view = this.view
    }

    createView() {
        return new EditorView(this.element, {
            state: this.createState(),
        })
    }

    createState() {
        return EditorState.create({
            schema: this.schema,
            doc: this.createDocument(this.options.content),
            plugins: [
                ...this.plugins,
                new Plugin({
                    key: new PluginKey("editable"),
                    props: {
                        editable: () => this.options.editable,
                    },
                }),
            ],
        })
    }

    setParentComponent(component = null) {
        return
    }
}

/**
 * Compute all diffRows.
 *
 * The algorithm is to loop until all left and right Nodes have been consumed:
 * - Take the next left node
 * - Consume all changes that are before the end of this next node
 * - Find the number of left Nodes affected by these changes (0, 1 or more)
 * - Find the number of right Nodes affected by these changes (0, 1 or more)
 * - Consume those left/right Nodes
 * - Create left/right Editors with those Nodes
 * - Next loop iteration
 */
class DiffRowsComputer {
    constructor(leftDoc, rightDoc, allLeftChanges, allRightChanges) {
        this.leftDoc = leftDoc
        this.rightDoc = rightDoc
        this.allLeftChanges = allLeftChanges
        this.allRightChanges = allRightChanges

        this.diffRows = []

        // All the top-level nodes in the left document
        this.allLeftNodes = this.leftDoc.content.content
        // All the top-level nodes in the right document
        this.allRightNodes = this.rightDoc.content.content
        // DocDiff.changes are already sorted by the position of their steps, from 0 to the end of the document.
        // We create a copied array, that we'll be used as a FIFO queue,
        // where we'll consume the changes as we progress in the loop.
        this.leftRemainingChanges = [...this.allLeftChanges]
        // Same for the right side
        this.rightRemainingChanges = [...this.allRightChanges]
        // Number of Nodes from the left that have already been consumed
        this.leftNodeIndex = 0
        // Number of Nodes from the right that have already been consumed
        this.rightNodeIndex = 0
        // A prosemirror Position of all the content already consumed in the left side
        this.leftPositionOffset = 0
        // A prosemirror Position of all the content already consumed in the right side
        this.rightPositionOffset = 0
    }

    computeDiffRows() {
        if (this.allLeftNodes.length < BLOCKING_THRESHOLD) {
            this.iterateRowsBlocking()
            return Promise.resolve(this.diffRows)
        } else {
            return new Promise((resolve, reject) => {
                setTimeout(() => this.iterateRowsNonBlocking(resolve), 0)
            })
        }
    }

    finalize() {
        // Here we handle a special-case : when there's added Node(s) at the end of the document,
        // but the change has been rejected, there won't be any Node neither in left or right.
        // We need to add an empty row to still display the Change, so the user can still toggle the Change
        if (this.leftRemainingChanges.length) {
            this.diffRows.push({
                leftEditor: null,
                rightEditor: null,
                changes: this.leftRemainingChanges,
                id: getRandomId(),
            })
        }

        // Freezing the array is VERY IMPORTANT for performances.
        // It prevents Vue.js to walk into the whole ( very huge ) diff rows to enable reactivity
        this.diffRows = Object.freeze(this.diffRows)
    }

    iterateRowsBlocking() {
        while (
            this.leftNodeIndex < this.allLeftNodes.length ||
            this.rightNodeIndex < this.allRightNodes.length
        ) {
            // One iteration of the loop
            this.computeOneRow()
        }

        // Terminal case : resolve the promise
        this.finalize()
    }

    iterateRowsNonBlocking(resolve) {
        let i = 0

        while (
            this.leftNodeIndex < this.allLeftNodes.length ||
            this.rightNodeIndex < this.allRightNodes.length
        ) {
            // One iteration of the loop
            this.computeOneRow()

            i++
            if (i >= CHUNK_SIZE) {
                // Launch next iteration, if there's still some Node to consume
                setTimeout(() => this.iterateRowsNonBlocking(resolve), 0)
                return
            }
        }

        // Terminal case : finalize and resolve the promise
        this.finalize()
        resolve(this.diffRows)
    }

    computeOneRow() {
        let leftChanges = [],
            rightChanges = [],
            acceptedLeftChanges = [],
            shiftedChanges = [],
            nbLeftNodes = 0,
            nbRightNodes = 0,
            leftNodes = [],
            rightNodes = [],
            leftNodesSize = 0,
            rightNodesSize = 0,
            leftEditor = null,
            rightEditor = null,
            nextLeftNode = this.allLeftNodes[this.leftNodeIndex],
            endOfNextNode,
            hasAddedContent = false,
            hasRemovedContent = false

        // Find all changes that are before the end of this next node
        if (nextLeftNode) {
            endOfNextNode = this.leftPositionOffset + nextLeftNode.nodeSize
            while (
                this.leftRemainingChanges.length &&
                this.leftRemainingChanges[0].step.from < endOfNextNode
            ) {
                leftChanges.push(this.leftRemainingChanges.shift())
            }
        }
        // We reached the end of the left nodes, but there may still be nodes on the right side
        else if (this.leftRemainingChanges.length > 0) {
            leftChanges.push(this.leftRemainingChanges.shift())
        }

        // Some changes may have been rejected
        acceptedLeftChanges = leftChanges.filter((change) => change.accepted)
        // Find the number of left/right Nodes affected by these changes
        // Also keep track of which side have been accepted, to display red/green background in the template
        for (let change of acceptedLeftChanges) {
            if (change.getAddedDOMFragment()) {
                hasAddedContent = true
            }
            if (change.getRemovedDOMFragment()) {
                hasRemovedContent = true
            }

            // For block counting, take into account only top-level block changes,
            // skip inner changes ( example : list items )
            let resolvedPos = this.leftDoc.resolve(change.step.from)
            if (resolvedPos.depth > 0) {
                // Special case for top-level paragraph cutting
                if (resolvedPos.depth == 1 && resolvedPos.parent.type.name == "paragraph") {
                    nbLeftNodes += Math.max(change.removedBlockLength, 1)
                    nbRightNodes += Math.max(change.addedBlockLength, 1)
                }
            } else {
                nbLeftNodes += change.removedBlockLength
                nbRightNodes += change.addedBlockLength
            }
        }

        // Special cases of counting are handled here.
        // TODO : Is there a different block counting to avoid those 3 tests ?
        if (nbLeftNodes == 0 && nbRightNodes == 0) {
            nbLeftNodes = nbRightNodes = 1
        } else if (nbLeftNodes > 0 && nbRightNodes == 0 && hasAddedContent) {
            nbRightNodes = 1
        } else if (nbLeftNodes == 0 && nbRightNodes > 0 && hasRemovedContent) {
            nbLeftNodes = 1
        }

        /***********************
         * Left side ( old document )
         ************************/
        if (nbLeftNodes) {
            leftNodes = this.getSomeLeftNodes(nbLeftNodes)
            leftNodesSize = _.sum(leftNodes.map((node) => node.nodeSize))
            ;({ editor: leftEditor, shiftedChanges } = this.createRowEditor(
                leftNodes,
                acceptedLeftChanges,
                this.leftPositionOffset,
            ))
            leftEditor.extensions.options.DiffAndMerge.publishChanges(shiftedChanges, {
                showInsertions: false,
            })
        }
        /***********************
         * Right side ( new document )
         ************************/
        if (nbRightNodes) {
            rightNodes = this.getSomeRightNodes(nbRightNodes)
            rightNodesSize = _.sum(rightNodes.map((node) => node.nodeSize))
            // Find the right changes corresponding to the Nodes we're displaying in this diffRow
            while (
                this.rightRemainingChanges.length &&
                this.rightRemainingChanges[0].step.from < this.rightPositionOffset + rightNodesSize
            ) {
                rightChanges.push(this.rightRemainingChanges.shift())
            }
            ;({ editor: rightEditor, shiftedChanges } = this.createRowEditor(
                rightNodes,
                rightChanges,
                this.rightPositionOffset,
            ))
            rightEditor.extensions.options.DiffAndMerge.publishChanges(shiftedChanges, {
                isInverted: true,
                showDeletions: false,
            })
        }

        // We have all the information we need for this diffRow, create it
        this.diffRows.push({
            leftEditor,
            rightEditor,
            changes: leftChanges,
            hasAddedContent,
            hasRemovedContent,
            id: getRandomId(),
        })

        // Update our position offsets
        this.leftPositionOffset = this.leftPositionOffset + leftNodesSize
        this.rightPositionOffset = this.rightPositionOffset + rightNodesSize
    }

    // Take N nodes from the left document, beginning from the current left node index
    getSomeLeftNodes(howMuch) {
        let nodes = this.allLeftNodes.slice(this.leftNodeIndex, this.leftNodeIndex + howMuch)
        this.leftNodeIndex += howMuch
        return nodes
    }
    // Take N nodes from the right document, beginning from the current right node index
    getSomeRightNodes(howMuch) {
        let nodes = this.allRightNodes.slice(this.rightNodeIndex, this.rightNodeIndex + howMuch)
        this.rightNodeIndex += howMuch
        return nodes
    }

    /**
     * Given a prosemirror Node corresponding to one paragraph,
     * create a Tiptap Editor to display this Node.
     * New Change objects will be created, with step positions shifted, to be displayed
     * inside this new editor.
     */
    createRowEditor(nodes, changes = [], positionOffset = 0) {
        let editor = new DiffRowEditor({
            extensions: itemContentSchema.getExtensions(),
            editable: false,
            content: {
                type: "doc",
                content: nodes.map((node) => node.toJSON()),
            },
            injectCSS: false, // VERY IMPORTANT for performances !!
        })

        let shiftedChanges = [],
            shiftedStep
        for (let change of changes) {
            let { step, sliceAdded, sliceRemoved } = change
            shiftedStep = Step.fromJSON(editor.schema, step.toJSON())
            shiftedStep.from -= positionOffset
            shiftedStep.to -= positionOffset
            shiftedChanges.push(new Change(shiftedStep, sliceAdded, sliceRemoved))
        }
        return { editor, shiftedChanges }
    }
}

export { DiffRowsComputer }
