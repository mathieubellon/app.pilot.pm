<template>
<div class="AnnotatableImage">
    <div
        class="AnnotatableImage__annotationLayer"
        :class="{ editable: !readOnly }"
        ref="layer"
        @mouseout="onMouseoutLayer"
        @mouseover="onMouseoverLayer"
    >
        <img
            class="AnnotatableImage__img"
            ref="image"
            :src="src"
        />

        <canvas
            v-show="selectionCanvasVisible"
            :style="canvasStyle"
            ref="selectionCanvas"
            :height="imageHeight"
            :width="imageWidth"
        />

        <canvas
            class="AnnotatableImage__viewCanvas"
            :class="{
                focus: showHint,
                unfocus: !showHint,
            }"
            :style="canvasStyle"
            ref="viewCanvas"
            :height="imageHeight"
            :width="imageWidth"
            @click="onClickCanvas"
            @mousedown="onMousedownCanvas"
            @mousemove="onMousemoveCanvas"
            @mouseup="onMouseupCanvas"
        />

        <div
            v-show="showHint && !readOnly"
            class="AnnotatableImage__hint"
        >
            <div class="AnnotatableImage__hintMsg">Click and Drag to Annotate</div>
            <div
                class="AnnotatableImage__hintIcon"
                style="pointer-events: auto"
            ></div>
        </div>

        <div
            v-show="annotationPopperVisible"
            class="popper"
            ref="annotationPopper"
        >
            <div
                v-if="annotationManager"
                class="AnnotatableImage__Annotation"
            >
                <AnnotationElement
                    v-if="!annotation.resolved"
                    v-for="annotation in annotationManager.selectedAnnotations"
                    :annotation="annotation"
                    :annotationManager="annotationManager"
                    :key="annotation.id"
                    :readOnly="readOnly"
                />
            </div>
            <div
                class="popper__arrow"
                x-arrow=""
            ></div>
        </div>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import $ from "jquery"
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import Popper from "popper.js"
import PopperUtils from "popper.js/dist/esm/popper-utils.js"

import { sanitizeCoordinates } from "./utils.js"
import { Shape, ShapeType, Units } from "./shape/shape.js"
import { RectDragSelector } from "./selection/rectDragSelector.js"
import ImageAnnotationsManager from "./ImageAnnotationsManager"
import AnnotationElement from "../AnnotationElement"
import { ItemPositioner } from "@js/items/itemsUtils"

export default {
    name: "AnnotatableImage",
    components: {
        AnnotationElement,
    },
    props: {
        src: String,
        annotations: Object,
        annotationsKey: String,
        readOnly: {
            type: Boolean,
            default: false,
        },
    },
    data: () => ({
        ready: false,
        imageHeight: 0,
        imageWidth: 0,
        imageOffset: { top: 0, left: 0 },

        selector: null,
        annotationManager: null,

        isDragging: false,
        selectionCanvasVisible: false,
        annotationPopperVisible: false,
        showHint: false,
    }),
    computed: {
        ...mapGetters("itemDetail", ["isHistoryPanelOpen"]),
        ...mapState("itemContentForm", ["myRealtimeUser"]),
        canvasStyle() {
            return {
                width: this.imageWidth + "px",
                height: this.imageHeight + "px",
            }
        },
        annotationPopperPositionRect() {
            // There should be either a single annotation selected, or none
            let annotation = this.annotationManager.selectedAnnotations[0]

            if (annotation && annotation.shape && annotation.shape.pixelGeometry) {
                return annotation.shape.pixelGeometry
                    .getBoundingRect()
                    .translate(this.imageOffset.left, this.imageOffset.top)
                    .getViewportBoundingRect()
            } else {
                return { top: 0, right: 0, bottom: 0, left: 0, width: 0, height: 0 }
            }
        },
        boundariesElement() {
            return PopperUtils.getScrollParent(this.$el)
        },
    },
    methods: {
        ...mapMutations("itemContentForm", ["registerAnnotationManager"]),
        computeImageDimensions() {
            if (!this.$refs.image) return
            this.imageHeight = this.$refs.image.clientHeight
            this.imageWidth = this.$refs.image.clientWidth
            this.imageOffset = $(this.$refs.image).offset()
        },
        init() {
            let annotator = this

            // Reactive properties
            this.computeImageDimensions()
            this.selector = new RectDragSelector()

            // Non reactive properties
            this.viewCanvas = this.$refs.viewCanvas
            this.selectionCanvas = this.$refs.selectionCanvas

            this.g2dView = this.viewCanvas.getContext("2d")
            this.g2dSelection = this.selectionCanvas.getContext("2d")

            // Setup the popperJs where annotation will show up
            let popperReference = {
                getBoundingClientRect() {
                    return annotator.annotationPopperPositionRect
                },
                get clientWidth() {
                    return annotator.annotationPopperPositionRect.width
                },
                get clientHeight() {
                    return annotator.annotationPopperPositionRect.height
                },
            }

            this.popperJS = new Popper(popperReference, this.$refs.annotationPopper, {
                placement: "right",
                modifiers: {
                    preventOverflow: {
                        boundariesElement: this.boundariesElement,
                    },
                    flip: {
                        behavior: ["right", "top", "bottom", "left"],
                        boundariesElement: this.boundariesElement,
                    },
                },
            })

            // Render the initial annotations
            this.renderAnnotations()

            this.ready = true
        },

        renderAnnotations() {
            if (!this.annotationManager) {
                return
            }
            // This will redraw the annotations
            this.annotationManager.setAnnotations(
                this.annotations ? this.annotations[this.annotationsKey] : {},
            )
        },

        redraw() {
            // Ensure the canvas always has the right dimensions.
            // This is useful if the image were hidden at the time of init,
            // for example when displaying an Item version.
            this.computeImageDimensions()

            // Wait for the image width/height to be applied on the canvas
            // to actually draw on the canvas.
            this.$nextTick(() => {
                // The image is not loaded yet, so there's no canvas, we cannot redraw
                if (!this.g2dView) {
                    return
                }

                this.g2dView.clearRect(0, 0, this.imageWidth, this.imageHeight)
                this.g2dSelection.clearRect(0, 0, this.imageWidth, this.imageHeight)

                _.forEach(this.annotationManager.annotations, (annotation) => {
                    if (annotation.resolved) {
                        return
                    }

                    // Re-init the shape object at each re-draw, to ensure the pixel geometry is correct
                    annotation.shape = Shape.fromAnnotation(annotation, this)

                    this.selector.drawShape(
                        this.g2dView,
                        annotation.shape,
                        this.annotationManager.selectedAnnotations.indexOf(annotation) > -1,
                    )
                })

                if (this.annotationManager.annotationInCreation) {
                    this.selector.drawShape(
                        this.g2dView,
                        this.annotationManager.annotationInCreation.shape,
                        true,
                    )
                }

                // Update the annotation popper position
                this.popperJS.scheduleUpdate()
            })
        },

        showAnnotationPopper() {
            this.annotationPopperVisible = true
            this.$nextTick(() => {
                if (this.popperJS) this.popperJS.scheduleUpdate()
            })
        },

        hideAnnotationPopper() {
            this.annotationPopperVisible = false
            this.$nextTick(() => {
                if (this.popperJS) this.popperJS.scheduleUpdate()
            })
        },

        onMouseoverLayer() {
            this.showHint = true
        },
        onMouseoutLayer() {
            this.showHint = false
        },
        // Draw selection
        onMousemoveCanvas(event) {
            if (!this.isDragging || this.readOnly) return

            this.g2dSelection.clearRect(0, 0, this.imageWidth, this.imageHeight)

            let coords = sanitizeCoordinates(event, this.viewCanvas)
            this.selector.updateSelection(this.g2dSelection, coords)
        },
        // Start selection
        onMousedownCanvas(event) {
            if (!this.selector) {
                return
            }

            this.isDragging = true

            // Hide the popper if it was displayed
            this.hideAnnotationPopper()
            // Hide previous annotation creation
            this.annotationManager.cancelCommentEdition()

            this.selectionCanvasVisible = true

            $(document.body).css("-webkit-user-select", "none")
            let coords = sanitizeCoordinates(event, this.viewCanvas)
            this.selector.startSelection(coords)
        },
        // Stop selection
        onMouseupCanvas(event) {
            if (!this.selector) {
                return
            }

            this.isDragging = false
            $(document.body).css("-webkit-user-select", "auto")

            let pixelGeometry = this.selector.getGeometry()
            // Selection completed
            if (pixelGeometry) {
                let shape = new Shape({
                    type: ShapeType.RECTANGLE,
                    geometry: pixelGeometry.toFractionCoordinates(
                        this.imageWidth,
                        this.imageHeight,
                    ),
                    pixelGeometry: pixelGeometry,
                    units: Units.FRACTION,
                })
                // This will also trigger a redraw, no need to do it here
                this.annotationManager.startAnnotationCreation(shape)
            }
            // Selection cancel
            else {
                this.g2dSelection.clearRect(0, 0, this.imageWidth, this.imageHeight)
                this.selectionCanvasVisible = false
            }

            this.selector.stopSelection()
        },
        // Highlight annotation
        onClickCanvas(event) {
            // Dont trigger annotation highlighting if we're in selection mode
            if (this.selectionCanvasVisible) {
                return
            }

            let coords = sanitizeCoordinates(event, this.viewCanvas)
            this.annotationManager.selectAnnotationsAtPosition(coords)
        },
    },
    watch: {
        /**
         * When the annotation change, make a restoration on the annotationManager
         */
        annotations: {
            handler() {
                if (!this.ready) return
                this.renderAnnotations()
            },
            deep: true,
        },
        /**
         * We need to trigger a rendering when the version panel is opened.
         * When it's hidden, the image dimensions are 0, so we need to recompute them then redraw.
         */
        isHistoryPanelOpen() {
            if (!this.ready) return
            this.renderAnnotations()
        },
        /**
         * When the selected annotation change, change popup visibility
         */
        "annotationManager.selectedAnnotations"(selectedAnnotations) {
            if (!this.ready) return
            if (selectedAnnotations.length) this.showAnnotationPopper()
            else this.hideAnnotationPopper()
        },
    },
    mounted() {
        // Setup the annotation manager immediately
        // We need to to this setup as soon as the component is created,
        // so the annotationManager is available in the $store immediatly,
        // to access it for scrolling
        this.annotationManager = new ImageAnnotationsManager(this.myRealtimeUser, this)
        this.annotationManager.on("update", (annotations) => {
            this.$emit("annotations", {
                annotationsKey: this.annotationsKey,
                annotations,
            })
        })
        this.registerAnnotationManager({
            key: this.annotationsKey,
            annotationManager: this.annotationManager,
            readOnly: this.readOnly,
        })

        // Move the popper to the end of the app to make positioning easier
        $(this.$refs.annotationPopper).appendTo("body")

        // We need to wait for the image to load before initializing the annotator
        $(this.$refs.image).on("load", () => {
            this.init()
        })

        this.itemPositioner = new ItemPositioner(this.annotationsKey, this.redraw)
        // Override the redraw callback for scrolling
        this.itemPositioner.callbacks.onScroll = () => {
            // We don't need to redraw on the canvas, only to recompute the image position
            this.computeImageDimensions()
            // Then we should re-render the annotations
            this.$nextTick(() => {
                if (this.popperJS) this.popperJS.scheduleUpdate()
            })
        }
    },
    beforeDestroy() {
        if (this.popperJS) {
            this.popperJS.destroy()
        }
        this.itemPositioner.detachEventHandlers()
        $(this.$refs.image).off("load")

        // Elements appended to body must be removed manually, because Vue.js won't do it automatically.
        if (this.$refs.annotationPopper) {
            this.$refs.annotationPopper.remove()
        }
    },
}
</script>

<style lang="scss">
@import "~@sass/business/items_vars.scss";

%opacityFade {
    -moz-transition-property: opacity;
    -moz-transition-duration: 0.5s;
    -moz-transition-delay: 0s;
    -webkit-transition-property: opacity;
    -webkit-transition-duration: 0.5s;
    -webkit-transition-delay: 0s;
    -o-transition-property: opacity;
    -o-transition-duration: 0.5s;
    -o-transition-delay: 0s;
    transition-property: opacity;
    transition-duration: 0.5s;
    transition-delay: 0s;
}

.AnnotatableImage__annotationLayer {
    display: inline-block;
    position: relative;

    &.editable {
        cursor: crosshair;
    }
}

.AnnotatableImage__img {
    max-width: 100%;
    width: 100%; // For IE11
    line-height: 0;
    border-radius: 0;
    height: auto;
}

.AnnotatableImage canvas {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 10;
}

.AnnotatableImage__viewCanvas {
    @extend %opacityFade;

    &.focus {
        opacity: 1;
    }
    &.unfocus {
        opacity: 0.4;
    }
}

.AnnotatableImage__Annotation {
    padding: 5px;
    width: $widthDecorationBox;
    cursor: default;
    // Reset base font-size to be the same in editable and read-only mode
    font-size: 17px;
}

.AnnotatableImage__hint {
    position: absolute;
    white-space: nowrap;
    pointer-events: none;
}

.AnnotatableImage__hintMsg {
    @extend %opacityFade;

    background-color: rgba(0, 0, 0, 0.5);
    margin: 4px;
    padding: 8px 15px 8px 30px;
    font-family: "lucida grande", tahoma, verdana, arial, sans-serif;
    line-height: normal;
    font-size: 12px;
    color: #fff;
    border-radius: 4px;
    -moz-border-radius: 4px;
    -webkit-border-radius: 4px;
    -khtml-border-radius: 4px;
}

.AnnotatableImage__hintIcon {
    position: absolute;
    top: 6px;
    left: 5px;
    background: url("feather_icon.png");
    background-repeat: no-repeat;
    width: 19px;
    height: 22px;
    margin: 2px 4px 0px 6px;
}
</style>
