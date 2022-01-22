/**
 * A 'domain class' implementation of the image annotation interface.
 */
export class ImageAnnotation {
    constructor({ id, shape, mainComment, comments, resolved, resolvedBy }) {
        this.id = id // Unique id of this annotation
        this.shape = shape // The shape on the image
        this.mainComment = mainComment // The initial comment of the annotation, that cannot be deleted
        this.comments = comments // List of other comment
        this.resolved = resolved // Set to true to hide the annotation
        this.resolvedBy = resolvedBy || null // When resolved == true, keep track of the user who resolved
    }

    resolve(resolvedBy) {
        this.shape = null
        this.resolved = true
        this.resolvedBy = resolvedBy
    }
}
