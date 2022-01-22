import _ from "lodash"

export const NODE_TYPES = {
    item: "item",
    folder: "folder",
}

export function hasDescendant(folder, maybeDescendant) {
    while (maybeDescendant) {
        if (maybeDescendant.parent == folder) {
            return true
        }
        maybeDescendant = maybeDescendant.parent
    }
    return false
}

export function flattenHierarchy(nodes) {
    return _.flatten(
        nodes.map((node) => {
            if (node.type == NODE_TYPES.item) {
                return node
            }
            if (node.type == NODE_TYPES.folder) {
                return [node, ...flattenHierarchy(node.nodes)]
            }
        }),
    )
}

export function countItemsInHierarchy(nodes) {
    return _.sum(
        nodes.map((node) => {
            if (node.type == NODE_TYPES.item) {
                return 1
            }
            if (node.type == NODE_TYPES.folder) {
                return countItemsInHierarchy(node.nodes)
            }
        }),
    )
}

export function getFolderPath(folder) {
    let path = []
    while (folder.level >= 0) {
        path.push(folder.name)
        folder = folder.parent
    }
    path.reverse()
    return path
}

export function getItemPathInHierarchy(nodes, item_id) {
    for (let node of nodes) {
        if (node.type == NODE_TYPES.item && node.id == item_id) {
            return []
        }
        if (node.type == NODE_TYPES.folder) {
            let found = getItemPathInHierarchy(node.nodes, item_id)
            if (found) {
                return [node.name, ...found]
            }
        }
    }
    return null
}
