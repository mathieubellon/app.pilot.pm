import _ from "lodash"

/**
 * Regroup the data needed to display an item :
 *  - The content for read-only display
 *  - The annotations
 *  - The item version
 *  - The diff data when diffing
 *  - If the diff allow a merge (for item reviews)
 *
 *  It's a common interface to unify data from different source :
 *  - Current Item version (editable)
 *  - An Edit Session, which is a read-only old version
 *  - An Item Sharing, which is a forked version of an item
 *  - A diff between two versions
 *  - A diff with an Item Sharing
 */
export class ItemReadOnly {
    constructor({
        content = {},
        contentSchema = [],
        annotations = {},
        version = "",
        isDiff = false,
        fieldDiffs = {},
        diffVersions = {},
    }) {
        // The actual content
        this.content = content
        // The content schema
        this.contentSchema = contentSchema
        // The annotations
        this.annotations = annotations
        // The item version
        this.version = version

        this.isDiff = isDiff
        this.fieldDiffs = fieldDiffs
        // The left and right versions of the diff
        this.diffVersions = diffVersions
    }

    getSchema(name) {
        return _.find(this.contentSchema, (schema) => schema.name == name)
    }

    /**
     * Create an ItemReadOnly from an Item instance
     */
    static fromItem(item) {
        return new ItemReadOnly({
            content: item.content,
            contentSchema: item.item_type ? item.item_type.content_schema : [],
            annotations: item.annotations,
            version: item.version,
        })
    }

    /**
     * Create an ItemReadOnly from an EditSession instance
     */
    static fromEditSession(session) {
        return new ItemReadOnly({
            content: session.content,
            contentSchema: session.content_schema,
            annotations: session.annotations,
            version: session.version,
        })
    }

    /**
     * Create an ItemReadOnly from backend diff data
     */
    static fromDiff(backendDiff) {
        return new ItemReadOnly({
            contentSchema: backendDiff.content_schema,
            // Use the correct version for the reference, depending on the`swapped` value
            version: backendDiff.swapped ? backendDiff.version.left : backendDiff.version.right,
            isDiff: true,
            fieldDiffs: backendDiff.diff,
            diffVersions: backendDiff.version,
        })
    }
}
