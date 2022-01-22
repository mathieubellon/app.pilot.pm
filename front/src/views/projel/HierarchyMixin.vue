<script>
import _ from "lodash"
import { getRandomId, toLowerAlpha } from "@js/utils"
import { NODE_TYPES } from "@js/hierarchy"

export default {
    name: "HierarchyMixin",
    data: () => ({
        hierarchy: [],
        items: {},
    }),
    computed: {
        virtualRootFolder() {
            return {
                type: NODE_TYPES.folder,
                name: "__ROOT__",
                nodes: [],
                parent: null,
                level: -1,
                isOpen: true,
            }
        },
    },
    methods: {
        getRepr(node) {
            if (node.type == NODE_TYPES.item) {
                let item = this.items[node.id]
                return item ? item.title : _.toString(node.id)
            }
            if (node.type == NODE_TYPES.folder) {
                return node.name
            }
        },

        prepareNode(node, parent) {
            let isCreation = !node.nodeId
            // Only for node creation
            if (isCreation) {
                node.nodeId = getRandomId()
            }
            // For creation and updates
            node.level = parent.level + 1
            node.parent = parent
            if (node.type == NODE_TYPES.folder) {
                if (isCreation) {
                    node.isOpen = false
                }
                this.prepareHierarchy(node.nodes, node)
            }
            return node
        },

        prepareHierarchy(nodes, parent = null) {
            for (let node of nodes) {
                this.prepareNode(node, parent)
            }
        },

        sortHierarchy(nodes) {
            nodes.sort((node1, node2) => {
                if (node1.type != node2.type) {
                    return node1.type == NODE_TYPES.folder ? -1 : 1
                } else {
                    return toLowerAlpha(this.getRepr(node1)).localeCompare(
                        toLowerAlpha(this.getRepr(node2)),
                    )
                }
            })
            for (let node of nodes) {
                if (node.type == NODE_TYPES.folder) {
                    this.sortHierarchy(node.nodes)
                }
                // Folders are all sorted first, so we can stop when we're done iterating over the folders
                else {
                    break
                }
            }
        },

        initHierarchy(hierarchy) {
            // Don't set this.hierarchy just yet,
            // because we need to add some attributes in this.prepareHierarchy,
            // so Vue can make them reactive when we assign the hierarchy in this.hierarchy.
            hierarchy = _.cloneDeep(hierarchy || [])
            this.prepareHierarchy(hierarchy, this.virtualRootFolder)
            this.sortHierarchy(hierarchy)
            this.virtualRootFolder.nodes = hierarchy
            // Ok, now we're ready to set this.hierarchy
            this.hierarchy = hierarchy
        },
    },
}
</script>
