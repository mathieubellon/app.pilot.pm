<script>
import _ from "lodash"
import $ from "jquery"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import { NODE_TYPES, hasDescendant, flattenHierarchy } from "@js/hierarchy"
import { Draggable } from "@shopify/draggable/lib/es5/draggable.bundle"
import HierarchyMixin from "@views/projel/HierarchyMixin"

const NODE_HEIGHT = 44

export default {
    name: "ProjelHierarchyMixin",
    mixins: [HierarchyMixin],
    data: () => ({
        highlightedNode: null,
        folderInEdition: null,
        folderValidationError: null,
        folderInDeletion: null,
        parentFolderForAddItem: null,
        nameEdited: null,

        /***********************
         * Drag'n'drop data
         ************************/
        dropSourceNode: null,
        dropTargetFolder: null,

        hasDescendant,
        NODE_HEIGHT,
    }),
    computed: {
        ...mapState("projelDetail", ["projel", "lastFetchProjelPromise"]),
        ...mapGetters("users", ["myPermissions"]),

        isHierarchyEmpty() {
            return this.hierarchy.length === 0
        },

        flattenedVisibleNodes() {
            // To be implemented by components that use this mixin
            return []
        },

        rootIsHighlighted() {
            return (
                this.dropSourceNode != null &&
                this.dropSourceNode.parent != this.virtualRootFolder &&
                this.dropTargetFolder == this.virtualRootFolder
            )
        },
    },
    methods: {
        ...mapActions("projelDetail", ["partialUpdateProjel"]),

        getItem(node) {
            return this.items[node.id] || {}
        },

        saveHierarchy() {
            this.partialUpdateProjel({
                hierarchy: this.cleanHierarchyForSaving(this.hierarchy),
            })
        },

        scrollToNode(node) {
            let nodeIndex = this.flattenedVisibleNodes.indexOf(node)
            let top = nodeIndex * NODE_HEIGHT
            $(".vue-recycle-scroller__item-wrapper").parent().scrollTop(top)
        },

        /***********************
         * Nodes management. Don't call this.saveHierarchy() from any of those methods !
         ************************/

        cleanHierarchyForSaving(nodes) {
            return nodes.map((node) => {
                if (node.type == NODE_TYPES.item) {
                    return {
                        type: node.type,
                        id: node.id,
                    }
                }
                if (node.type == NODE_TYPES.folder) {
                    return {
                        type: node.type,
                        name: node.name,
                        nodes: this.cleanHierarchyForSaving(node.nodes),
                    }
                }
            })
        },

        addNode(node, targetFolder) {
            this.prepareNode(node, targetFolder)
            targetFolder.nodes.unshift(node)
            this.sortHierarchy(targetFolder.nodes)
            // Close added folders if the target folder is closed
            if (!targetFolder.isOpen) {
                this.closeFolder(targetFolder)
            }
        },

        removeNode(node) {
            let index = _.findIndex(node.parent.nodes, (n) => n.nodeId == node.nodeId)
            node.parent.nodes.splice(index, 1)
        },

        moveNode(node, targetFolder) {
            // Drop only on folders.
            // Don't drop on our own parent, we're already there.
            // Also, don't drop a folder inside its own sub hierarchy ( or themsleves ),
            // or you'll release the hell of cyclicity upon us !
            if (
                !node ||
                !targetFolder ||
                targetFolder.type != NODE_TYPES.folder ||
                node == targetFolder ||
                node.parent == targetFolder ||
                hasDescendant(node, targetFolder)
            ) {
                // NOPE Don't do it !!!
                return false
            }

            this.removeNode(node)
            this.addNode(node, targetFolder)
            this.openFolder(targetFolder)
            return true
        },

        stopNodeHighlightingAtNextClick(node) {
            setTimeout(
                () =>
                    $(window).one("click", () => {
                        if (this.highlightedNode == node) {
                            this.highlightedNode = null
                        }
                    }),
                200,
            )
        },

        /***********************
         * Folders management
         ************************/

        toggleFolderOpening(folderNode) {
            folderNode.isOpen ? this.closeFolder(folderNode) : this.openFolder(folderNode)
        },

        openFolder(folderNode, recursive = false) {
            // Opening a folder may not be recursive
            if (recursive) {
                for (let node of folderNode.nodes) {
                    if (node.type == NODE_TYPES.folder) {
                        this.openFolder(node, true)
                    }
                }
            }
            folderNode.isOpen = true
        },

        openAllFolders() {
            this.openFolder(this.virtualRootFolder, true)
        },

        closeFolder(folderNode) {
            // Closing a folder is always recursive
            for (let node of folderNode.nodes) {
                if (node.type == NODE_TYPES.folder) {
                    this.closeFolder(node)
                }
            }
            folderNode.isOpen = false
        },

        closeAllFolders() {
            this.closeFolder(this.virtualRootFolder)
            // Don't let the virtual root folder closed, this would hide everything !
            this.virtualRootFolder.isOpen = true
        },

        toggleFolder(node) {
            if (node.type == NODE_TYPES.folder) {
                node.isOpen ? this.closeFolder(node) : this.openFolder(node)
            }
        },

        createFolder(parent) {
            if (!this.myPermissions.is_admin) {
                return
            }

            let folder = {
                type: NODE_TYPES.folder,
                name: "",
                nodes: [],
                created: true,
            }
            this.addNode(folder, parent)
            this.highlightedNode = folder
            this.openFolder(parent)
            this.startNameEdition(folder)
            if (parent == this.virtualRootFolder) {
                this.scrollToNode(folder)
            }
        },

        deleteFolder(folderNode) {
            if (!this.myPermissions.is_admin) {
                return
            }

            for (let child of flattenHierarchy(folderNode.nodes)) {
                if (child.type == NODE_TYPES.item) {
                    this.moveNode(child, this.virtualRootFolder)
                }
            }
            this.removeNode(folderNode)
            this.saveHierarchy()
        },

        startNameEdition(folderNode) {
            if (!this.myPermissions.is_admin) {
                return
            }

            this.nameEdited = folderNode.name
            this.folderInEdition = folderNode
            this.folderValidationError = null
            this.$nextTick(() => {
                $(this.$refs.nameEditionInput).focus()
            })
        },

        validateFolderName() {
            this.folderValidationError = null

            // Prevent duplicate names in the same parent folder
            let isDuplicate = this.folderInEdition.parent.nodes.find(
                (n) => n != this.folderInEdition && n.name == this.nameEdited,
            )
            if (isDuplicate) {
                this.folderValidationError = this.$t("folderValidationError.duplicate")
            }
            // Prevent unnamed folder
            if (!this.nameEdited) {
                this.folderValidationError = this.$t("folderValidationError.unnamed")
            }
        },

        endNameEdition() {
            if (!this.folderInEdition) {
                return
            }

            this.validateFolderName()
            if (this.folderValidationError) {
                this.$nextTick(() => {
                    let popper = this.$refs.folderValidationPopper
                    if (_.isArray(popper)) {
                        popper = popper[0]
                    }
                    popper.showPopper()
                })
                return
            }

            // No validation error, we can go on
            let folder = this.folderInEdition
            folder.name = this.nameEdited
            this.sortHierarchy(folder.parent.nodes)
            this.saveHierarchy()
            this.folderInEdition = null
            this.nameEdited = null

            this.stopNodeHighlightingAtNextClick(folder)
        },

        startFolderDeletion(node) {
            this.folderInDeletion = node
            this.$modal.show("deleteFolder")
        },

        confirmFolderDeletion() {
            this.deleteFolder(this.folderInDeletion)
            this.folderInDeletion = null
            this.$modal.hide("deleteFolder")
        },

        /***********************
         * Drag handlers
         ************************/

        getNodeFromDOMElement(element) {
            return this.flattenedVisibleNodes[$(element).attr("nodeIndex")]
        },

        onDragStart(event) {
            this.dropSourceNode = this.getNodeFromDOMElement(event.originalSource)
        },

        onDragOver(event) {
            let targetNode = this.getNodeFromDOMElement(event.over)
            this.dropTargetFolder = targetNode.type == NODE_TYPES.folder ? targetNode : null
        },
        onDragOut(event) {
            //this.dropTargetFolder = null
        },
        onDragOutContainer(event) {
            this.dropTargetFolder = this.virtualRootFolder
        },
        onDragStop(event) {
            let moved = this.moveNode(this.dropSourceNode, this.dropTargetFolder)
            if (moved) {
                this.saveHierarchy()
            }
            this.dropTargetFolder = null
            this.dropSourceNode = null
        },

        /***********************
         * Init
         ************************/

        setupDraggable() {
            this.draggable = new Draggable(
                document.querySelector("#ProjelHierarchy__DragContainer"),
                {
                    draggable: ".ProjelHierarchy__Draggable",
                    distance: 15,
                    delay: 150,
                    classes: {
                        "source:original": "ProjelHierarchy__DragSourceOriginal",
                        mirror: "ProjelHierarchy__DraggingMirror",
                    },
                    mirror: {
                        cursorOffsetX: 150,
                        appendTo: "body",
                    },
                },
            )
            this.draggable.on("drag:start", this.onDragStart)
            this.draggable.on("drag:over", this.onDragOver)
            this.draggable.on("drag:out", this.onDragOut)
            this.draggable.on("drag:out:container", this.onDragOutContainer)
            this.draggable.on("drag:stop", this.onDragStop)
        },
    },
    i18n: {
        messages: {
            fr: {
                createFolder: "Créer un dossier",
                folderValidationError: {
                    duplicate: "Ce nom est déjà utilisé",
                    unnamed: "Le dossier n'a pas de nom",
                },
            },
            en: {
                createFolder: "Create folder",
                folderValidationError: {
                    duplicate: "This name is already used",
                    unnamed: "The folder should have a name",
                },
            },
        },
    },
}
</script>

<style lang="scss">
.ProjelHierarchy__Draggable {
    cursor: grab;
}

#ProjelHierarchy__DragContainer {
    user-select: none;
}

.ProjelHierarchy__DragSourceOriginal {
    display: none !important;
}

.ProjelHierarchy__DraggingMirror {
    @apply bg-indigo-50 border border-indigo-500 rounded p-2 absolute;
    width: 300px;
}
</style>
