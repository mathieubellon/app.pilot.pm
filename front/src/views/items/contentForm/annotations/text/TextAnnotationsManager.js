/**
 * Annotations should always be in sync with the content when saved to the backend.
 *
 * We prevent the user to create/edit/delete annotations and comments while the content is being
 * edited, eg when the contentModel is dirty.
 */
import _ from "lodash"
import $ from "jquery"

import { TextSelection } from "prosemirror-state"
import { getRandomId } from "@js/utils.js"
import { TextAnnotation } from "./TextAnnotation"
import { annotationPluginKey } from "@richText/extensions/annotations"
import * as itemDecorationBoxes from "@js/items/itemDecorationBoxes"
import { scrollItemTo } from "@js/items/itemsUtils"
import BaseAnnotationsManager from "../BaseAnnotationsManager"

export default class TextAnnotationsManager extends BaseAnnotationsManager {
    constructor(user, pmView) {
        super(user)
        this.type = "text"
        this.pmView = pmView
    }

    /**
     * Redraw all annotation range into the prosemirror view
     */
    redraw() {
        if (!this.pmView) return

        // Don't dispatch through this.pmView.dispatch because that would trigger
        // the side-effects of dispatchTransaction, including the angular scope digest
        // which would cause some serious mess with slow browser (Internet Explorer...)
        let transaction = this.pmView.state.tr.setMeta(annotationPluginKey, {
            type: "redrawAnnotationDecorations",
        })
        let newState = this.pmView.state.apply(transaction)
        this.pmView.updateState(newState)
        //this.pmView.dispatch(transaction)

        itemDecorationBoxes.alignBoxes(this.pmView)
    }

    /**
     * Create a new annotation object
     */
    createAnnotation(annotationData, storeText = true) {
        let annotation = new TextAnnotation(annotationData)
        if (storeText) {
            this.storeSelectedTextOnAnnotation(annotation)
        }
        return annotation
    }

    /**
     * Begin the creation of a new annotation,
     * linked to the text positionned at the current selection in the editor
     */
    startAnnotationCreation() {
        // This one is very tricky, but critical.
        // On IE11, when the editor lose focus, the selection is reset
        // by the browser, which trigger a deluge of selection event by the
        // prosemirror event observer.
        // In turn, these events would bring hell on the angular cycle because of
        // dispatchTransaction.
        // We need to blur it manually ourselves, to prevent those events.
        // The deluge of events doesn't happen on modern browser because the event observer
        // is much cleaner, but the blur does not hurt them.
        $(this.pmView.dom).blur()

        // If there was another annotation in creation, cancel this creation
        if (this.annotationInCreation) {
            this.cancelCommentEdition()
        }

        // Assign a new random id for the new annotation
        let annotationId = getRandomId()
        // Get the selection from prosemirror
        let sel = this.pmView.state.selection
        // Init a new empty comment for the main comment
        let mainComment = this.makeCommentObject(null)
        // Create an empty annotation
        this.annotationInCreation = this.createAnnotation({
            id: annotationId,
            range: { from: sel.from, to: sel.to },
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
     * Get the annotations associated to the marks at the position, sorted by date desc.
     *
     * @param pos
     * @returns {Array.<*>}
     */
    findAnnotationsAt(pos) {
        return _.filter(this.annotations, function (annotation) {
            return annotation.range && annotation.range.from <= pos && annotation.range.to >= pos
        })
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
        // Wait for all decorations to be rendered
        // and scroll the edition panel to the decoration location
        setTimeout(
            () => {
                scrollItemTo({
                    $elem: $(".annotation-" + annotation.id),
                    adjustEditionPanel: true,
                    offset: 50, // We need to offset by the rich text menubar height
                })

                let pos = annotation.range.from

                // Trigger a selection in prosemirror, so the annotation boxes are displayed at the correct location
                // now, and also in the event of a window resize
                let newState = this.pmView.state.apply(
                    this.pmView.state.tr.setSelection(
                        TextSelection.create(this.pmView.state.doc, pos, pos),
                    ),
                )
                this.pmView.updateState(newState)

                // Now that the mark is visible, we can select the annotation
                this.selectAnnotations([annotation])
            },
            // Wait for the browser to render the decorations
            100,
        )
    }

    // Ensure the annotation can be applied at the given position
    canAnnotationBeCreated(annotation) {
        try {
            let checkSelectedText = this.pmView.state.doc.textBetween(
                annotation.range.from,
                annotation.range.to,
            )
            /*if (annotation.selectedText === checkSelectedText) {
                return true
            } else {
                console.warn("Position are valid but text differ / I can't find the correct text at this position", annotation)
                return false
            }*/
            return true
        } catch (e) {
            console.warn(
                "Positions (from and/or to) for this annotation does not exist in document",
                annotation,
            )
            return false
        }
    }

    /**
     * Store the selected text only if the annotation is not resolved
     *
     * @param annotation
     * @param document An optional prosemirror document from which the text should be refreshed.
     * If no document is provided, default to the current document of our view
     */
    storeSelectedTextOnAnnotation(annotation, document = null) {
        // Store the currently selected text only if the annotation is not resolved
        if (
            annotation &&
            !annotation.resolved &&
            !annotation.orphan &&
            annotation.range.from &&
            annotation.range.to
        ) {
            // If no document is provided, default to the current document of our view
            document = document || this.pmView.state.doc
            annotation.selectedText = document.textBetween(
                annotation.range.from,
                annotation.range.to,
            )
        }
    }

    /**
     * Keep up to date the selectedText attribute of each annotations
     * when the document change after a user input
     *
     * @param document An optional prosemirror document from which the text should be refreshed.
     * If no document is provided, default to the current document of our view
     */
    refreshAllSelectedText(document = null) {
        let annotations = [...Object.values(this.annotations), this.annotationInCreation]
        for (let annotation of annotations) {
            this.storeSelectedTextOnAnnotation(annotation, document)
        }
    }

    /**
     * Keep the annotation range in sync with the content, when the document is transformed.
     * This happens either when the user make some modifications to the document ( type or delete some text ),
     * or when we programmatically change the document ( during a review merge for example ).
     *
     * We use the prosemirror Transaction object to remap each annotation range to their new positions.
     *
     * @param transaction The prosemirror Transaction applied to the document
     */
    remapAfterTransaction(transaction) {
        this.mapAnnotations(transaction.mapping)

        // When the range have been updated, we can refresh the selected text
        // The transform has not yet been applied on this.pmView.state.doc
        // so we need to use the one from transaction.doc
        this.refreshAllSelectedText(transaction.doc)
    }

    /**
     * Apply a prosemirror mapping on each annotation position
     */
    mapAnnotations(mapping) {
        let annotations = [...Object.values(this.annotations), this.annotationInCreation]
        for (let annotation of annotations) {
            if (!annotation || annotation.orphan) {
                continue
            }

            // Map the new position
            // The 1/-1 parameter is to disable inclusive left/right
            let mapResultFrom = mapping.mapResult(annotation.range.from, 1),
                mapResultTo = mapping.mapResult(annotation.range.to, -1)

            // The annotated text does not exists anymore in the new document
            // We must resolve it
            if (mapResultFrom.deleted && mapResultTo.deleted) {
                this.resolveAnnotation(annotation)
            }
            // The annotation still exists, we can update its range
            else {
                annotation.setRange(mapResultFrom.pos, mapResultTo.pos)
            }
        }
    }
}
