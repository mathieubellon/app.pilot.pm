/**
 * A 'domain class' implementation of the text annotation interface.
 */
export class TextAnnotation {
    constructor({ id, range, mainComment, comments, resolved, resolvedBy, selectedText }) {
        this.id = id // Unique id of this annotation
        // Range in the form {'from': 0, 'to':1} if the annotation is marked into the editor
        this.range = {}
        // We need to make a new object to avoid keeping the same reference around.
        this.setRange(range.from, range.to)

        this.mainComment = mainComment // The initial comment of the annotation, that cannot be deleted
        this.comments = comments // List of other comment
        this.resolved = resolved // Set to true to remove the mark from the editor
        this.resolvedBy = resolvedBy || null // When resolved == true, keep track of the user who resolved
        this.selectedText = selectedText || null // The text highlighted by the annotation
    }

    resolve(resolvedBy) {
        this.range = { from: null, to: null }
        this.resolved = true
        this.resolvedBy = resolvedBy
    }

    setRange(from, to) {
        // We need to make a new object to avoid keeping the same reference around.
        this.range = { from, to }
    }
}
