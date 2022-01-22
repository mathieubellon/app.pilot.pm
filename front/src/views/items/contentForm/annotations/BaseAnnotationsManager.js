/**
 * Annotations should always be in sync with the content when saved to the backend.
 *
 * We prevent the user to create/edit/delete annotations and comments while the content is being
 * edited, eg when the contentModel is dirty.
 */
import _ from "lodash"
import Emitter from "@js/Emitter"

export default class BaseAnnotationsManager extends Emitter {
    constructor(user) {
        super()

        // The annotations linked to the content
        this.annotations = {}

        // Current user
        this.user = user

        this.selectedAnnotations = []
        this.editedComment = null
        this.annotationInCreation = null
    }

    redraw() {
        // To be implemented by sub classes
    }

    canAnnotationBeCreated() {
        // To be implemented by sub classes
        return true
    }

    emitUpdate() {
        this.emit("update", this.annotations)
    }

    /**
     * Make an object representing one comment from one user : { user, text, date }
     *
     * @param commentText The text of the comment
     * @param commentDate An optionnal date. Default to now.
     * @returns commentObject
     */
    makeCommentObject(commentContent, commentDate = null) {
        return {
            user: this.user,
            content: commentContent,
            date: commentDate ? commentDate : new Date(),
        }
    }

    /**
     * Check if the current user is the author of the comment
     *
     * @param comment The comment to check
     * @returns {boolean} True if the current user own the comment
     */
    ownComment(comment) {
        if (!comment || !this.user) {
            return false
        }
        return comment.user.id == this.user.id
    }

    /**
     * Begin the edition of a comment. Only the owner of a comment can edit it.
     *
     * @param comment The comment to edit
     */
    startCommentEdition(comment) {
        if (!this.ownComment(comment)) {
            return
        }

        this.editedComment = comment
    }

    cancelAnnotationCreation() {
        if (this.annotationInCreation) {
            this.annotationInCreation = null
            this.selectedAnnotations = []
        }
    }

    /**
     * Cancel the comment edition that is in progress
     */
    cancelCommentEdition() {
        // If the user cancel the creation of an annotation
        // then we must remove the marking in the editor
        if (this.annotationInCreation) {
            this.cancelAnnotationCreation()
            this.redraw()
        }

        this.editedComment = null
    }

    /**
     * Finalize the commenting process on an annotation, for both creation and edition.
     *
     * @param annotation
     */
    addOrEditAnnotationComment(annotation, commentContent) {
        if (!commentContent) {
            return
        }

        // Edit mode
        if (this.editedComment) {
            this.editedComment.content = commentContent
            this.editedComment.date = new Date()
        }
        // Add mode
        else {
            annotation.comments.push(this.makeCommentObject(commentContent))
        }

        // If the user validate a comment of an annotation in creation
        // then we must add it to the annotation list
        if (this.annotationInCreation) {
            this.annotations[this.annotationInCreation.id] = this.annotationInCreation
            this.annotationInCreation = null
        }

        this.editedComment = null

        // Please save the annotations
        this.emitUpdate()
    }

    /**
     * Remove one comment from the comment list of an annotation
     *
     * @param annotation The annotation where the comment belongs
     * @param commentIndex The index of the comment to remove
     */
    removeAnnotationComment(annotation, commentIndex) {
        if (annotation && annotation.comments[commentIndex]) {
            annotation.comments.splice(commentIndex, 1)
        }

        // Please save the annotations
        this.emitUpdate()
    }

    /**
     * Mark an annotation as resolved.
     * Resolved annotation will not be shown to the user anymore,
     * but are kept in the list for archiving
     *
     * @param annotation
     */
    resolveAnnotation(annotation) {
        annotation.resolve(this.user)

        // Change the array reference to trigger vue reactivity
        this.selectedAnnotations = this.selectedAnnotations.filter((ann) => ann.id != annotation.id)

        this.redraw()

        // Please save the annotations
        this.emitUpdate()
    }

    /**
     * Deselect all annotations from this annotation managers,
     * and also cancel the annotation in creation.
     */
    deselectAnnotations() {
        this.selectedAnnotations = []
        // If there was another annotation in creation, cancel this creation
        if (this.annotationInCreation) {
            this.cancelCommentEdition()
        }
    }

    /**
     * Select all annotations at a given position.
     * Position may be a prosemirror Position or a X/Y coordinates
     *
     * @param pos The position i
     */
    selectAnnotationsAtPosition(position) {
        this.cancelCommentEdition()
        this.selectAnnotations(this.findAnnotationsAt(position))
    }

    selectAnnotations(annotations, deselectOther = true) {
        this.emit("select", { annotations, deselectOther })
        // Stable display order
        this.selectedAnnotations = _.sortBy(
            annotations,
            (annotation) => annotation.mainComment.date,
        ).reverse()
        this.redraw()
    }

    /**
     * Set new annotations value, while trying to keep the context (displayed annotations)
     */
    setAnnotations(annotations) {
        // Remember the selected annotation id, to show them back after the restoration
        let selectedAnnotationsIds = this.selectedAnnotations.map((annotation) => annotation.id)
        let selectedAnnotations = []

        // Remove existing annotations
        this.annotations = {}

        // Recreate annotations from the snapshoted annotations
        _.forEach(annotations, (annotation) => {
            if (annotation.resolved || this.canAnnotationBeCreated(annotation)) {
                annotation = this.createAnnotation(annotation)
            } else {
                // If annotation cannot be recreated (because position are out of range or because the annotation saved Selectedtext
                // is not the same as the text between the position) then store them for processing
                annotation.orphan = true
            }

            this.annotations[annotation.id] = annotation

            // If this annotation were selected, select it again
            if (selectedAnnotationsIds.indexOf(annotation.id) > -1) {
                selectedAnnotations.push(annotation)
            }
        })

        if (this.annotationInCreation) {
            selectedAnnotations.push(this.annotationInCreation)
        }

        // This will trigger a redraw, no need to do it again
        this.selectAnnotations(selectedAnnotations, false)
    }
}
