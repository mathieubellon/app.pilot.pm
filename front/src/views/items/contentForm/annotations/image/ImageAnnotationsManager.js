/**
 * Annotations should always be in sync with the content when saved to the backend.
 *
 * We prevent the user to create/edit/delete annotations and comments while the content is being
 * edited, eg when the contentModel is dirty.
 */
import _ from "lodash"
import $ from "jquery"

import { getRandomId } from "@js/utils.js"
import { scrollItemTo } from "@js/items/itemsUtils"
import BaseAnnotationsManager from "../BaseAnnotationsManager"
import { ImageAnnotation } from "./ImageAnnotation"

export default class ImageAnnotationsManager extends BaseAnnotationsManager {
    constructor(user, annotator) {
        super(user)
        this.type = "image"
        this.annotator = annotator
    }

    redraw() {
        this.annotator.redraw()
    }

    /**
     * Create a new annotation object
     */
    createAnnotation(annotationData) {
        return new ImageAnnotation(annotationData)
    }

    /**
     * Begin the creation of a new annotation,
     * linked to the text positionned at the current selection in the editor
     */
    startAnnotationCreation(shape) {
        // If there was another annotation in creation, cancel this creation
        if (this.annotationInCreation) {
            this.cancelCommentEdition()
        }

        // Assign a new random id for the new annotation
        let annotationId = getRandomId()
        // Init a new empty comment for the main comment
        let mainComment = this.makeCommentObject(null)
        // Create an empty annotation
        this.annotationInCreation = this.createAnnotation({
            id: annotationId,
            shape,
            mainComment,
            comments: [],
            resolved: false,
        })
        // When the annotation is created, start immediatly the main comment edition
        this.startCommentEdition(mainComment)
        // Display it
        this.selectAnnotations([this.annotationInCreation])
    }

    /**
     * Returns the annotations at the specified X/Y coordinates, sorted by size, smallest first.
     *
     * @param {number} coords the Xx/ycoordinate
     * @return {Array.<Annotation>} the annotations sorted by size, smallest first
     */
    findAllAnnotationsAt(coords) {
        let intersectedAnnotations = []

        _.forEach(this.annotations, (annotation) => {
            if (annotation.resolved) return

            let shape = annotation.shape
            if (shape.pixelGeometry.intersects(coords)) {
                intersectedAnnotations.push(annotation)
            }
        })

        intersectedAnnotations.sort((left, right) => {
            return left.shape.geometry.getSize() - right.shape.geometry.getSize()
        })

        return intersectedAnnotations
    }

    /**
     * Select only the smallest shape at the coords
     *
     * @param coords
     */
    findAnnotationsAt(coords) {
        let annotations = this.findAllAnnotationsAt(coords)
        return annotations.length ? [annotations[0]] : []
    }

    /**
     * Scroll the view to the location of the annotated text on the document
     *
     * @param annotation The annotation to bring into the view
     */
    scrollToAnnotation(annotation) {
        if (!annotation) {
            return
        }

        // Wait for the annotator toi be ready (img is loaded) before triggering the selection
        let intervalId = setInterval(() => {
            if (this.annotator.ready) {
                clearInterval(intervalId)

                scrollItemTo({
                    $elem: $(this.annotator.$el),
                    adjustEditionPanel: true,
                })

                // Now that the mark is visible, we can select the annotation
                // Don't use the annotation param directly, because its pixelGeometry attribute is not set
                this.selectAnnotations([this.annotations[annotation.id]])
            }
        }, 50)
    }
}
