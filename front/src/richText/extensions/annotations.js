import _ from "lodash"
import $ from "jquery"

import { Plugin, PluginKey } from "tiptap"
import { Decoration, DecorationSet } from "prosemirror-view"

const annotationPluginKey = new PluginKey("annotationPlugin")

/**
 * When the annotation Decorations has been computed by the plugin,
 * we need to make a run to modify css classes to account for multiple annotations
 * on a single character.
 * We also append some overlay for the annotated images.
 *
 * @param pmView prosemirror EditorView
 */
function applyAnnotationStyle(pmView) {
    // If we mutate the DOM while prosemirror is observing it,
    // then prosemirror will consider this is a user input and fire a redraw.
    // Thus we must stop the DOM observing during annotation style application
    // to prevent an infinite redraw-loop
    pmView.domObserver.stop()

    // update the css class to reflect the number of annotation on one mark for superposed annotations
    // We do not use transparency but 4 css classes with 4 different yellows so we can't have, visually, more than 4 marks superposed
    $(".annotation", pmView.dom).each(function (index, annotationMark) {
        let $annotationMark = $(annotationMark)

        // Count the occurence of 'annotation'
        let annotationCount = $annotationMark
            .attr("class")
            .split(" ")
            .reduce(function (n, class_) {
                return n + class_.startsWith("annotation-")
            }, 0)

        let annotationClassName = "annotationStyle-" + annotationCount

        // Remove any old style
        $annotationMark.removeClass(
            "annotationStyle-1 annotationStyle-2 annotationStyle-3 annotationStyle-4",
        )
        // Add the new one
        $annotationMark.addClass(annotationClassName)

        // Add an overlay for images
        if ($annotationMark.is("img")) {
            $annotationMark.next(".img-annotation-overlay").remove()

            let pos = $annotationMark.position()
            $annotationMark.after(
                $("<span></span>")
                    .addClass("img-annotation-overlay")
                    .addClass(annotationClassName)
                    .width($annotationMark.width())
                    .height($annotationMark.height())
                    .css({ left: pos.left, top: pos.top }),
            )
        }
    })
    // Get back DOM observing
    pmView.domObserver.start()
}

function decorationForAnnotation(annotation) {
    return Decoration.inline(annotation.range.from, annotation.range.to, {
        class: "annotation annotation-" + annotation.id,
    })
}

/**
 * Prosemirror plugin that keep the annotations in sync with the content,
 * and compute the prosemirror Decorations needed to show the annotation positions.
 *
 * When there's a transformation that change a doc, remap the annotation ranges.
 */
function annotationPlugin(annotationManager) {
    return new Plugin({
        state: {
            key: annotationPluginKey,

            init: (config, state) => ({
                annotationDecorations: DecorationSet.empty,
            }),
            apply: (transaction, oldState) => {
                // Remap the annotation position when the document change
                if (transaction.docChanged) {
                    annotationManager.remapAfterTransaction(transaction)
                }

                // Recompute the decoration from the annotation state at each transaction
                let decorations = []
                _.forEach(annotationManager.annotations, (annotation) => {
                    if (!annotation.resolved && !annotation.orphan) {
                        decorations.push(decorationForAnnotation(annotation))
                    }
                })
                if (annotationManager.annotationInCreation) {
                    decorations.push(
                        decorationForAnnotation(annotationManager.annotationInCreation),
                    )
                }

                return {
                    annotationDecorations: DecorationSet.create(transaction.doc, decorations),
                }
            },
        },

        props: {
            decorations(state) {
                return this.getState(state).annotationDecorations
            },
        },

        // Recompute the annotation style after each view update,
        // because prosemirror may recreate the DOM without them
        view: () => {
            return {
                update: applyAnnotationStyle,
            }
        },
    })
}

export { annotationPlugin, annotationPluginKey }
