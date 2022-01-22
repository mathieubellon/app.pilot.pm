import _ from "lodash"
import { Shape, ShapeType } from "../shape/shape.js"
import { Rectangle } from "../shape/rectangle"

const DEFAULT_STYLE = {
    outline: "red",
    stroke: "red",
    fill: false,
    hi_outline: "#fff000",
    hi_stroke: "#fff000",
    hi_fill: false,
    outline_width: 2,
    stroke_width: 2,
    hi_outline_width: 2,
    hi_stroke_width: 2,
}

/**
 * The default selector: a simple click-and-drag rectangle selection tool.
 * @constructor
 */
export class RectDragSelector {
    constructor() {
        this.anchor = null
        this.head = null
    }

    /**
     * Selector API method: starts the selection at the specified coordinates.
     * @param {number} x the X coordinate
     * @param {number} y the Y coordinate
     */
    startSelection(coords) {
        this.anchor = coords
    }

    /**
     * Selector API method: update the selection coordinates when the mouse moves
     */
    updateSelection(g2d, coords) {
        this.head = coords

        let geometry = this.getGeometry()
        // This may happen when the rectangle size is to small ( <3px )
        if (!geometry) {
            return
        }

        this.drawShape(
            g2d,
            new Shape({
                type: ShapeType.RECTANGLE,
                pixelGeometry: geometry,
            }),
            false,
        )
    }

    /**
     * Selector API method: stops the selection.
     */
    stopSelection() {
        this.anchor = null
        this.head = null
    }

    /**
     * Selector API method: returns the currently edited geometry.
     * @return {Geometry | undefined} the shape
     */
    getGeometry() {
        if (
            this.head &&
            this.anchor &&
            Math.abs(this.head.x - this.anchor.x) > 3 &&
            Math.abs(this.head.y - this.anchor.y) > 3
        ) {
            return new Rectangle({
                x: this.anchor.x,
                y: this.anchor.y,
                width: this.head.x - this.anchor.x,
                height: this.head.y - this.anchor.y,
            })
        } else {
            return null
        }
    }

    /**
     * @param {Object} g2d graphics context
     * @param {Shape} shape the shape to draw
     * @param {boolean=} highlight if true, shape will be drawn highlighted
     */
    drawShape(g2d, shape, highlight) {
        if (shape.type != ShapeType.RECTANGLE) {
            return
        }

        let geom, stroke, fill, outline, outline_width, stroke_width
        let style = _.defaults({}, shape.style, DEFAULT_STYLE)

        if (highlight) {
            fill = style.hi_fill
            stroke = style.hi_stroke
            outline = style.hi_outline
            outline_width = style.hi_outline_width
            stroke_width = style.hi_stroke_width
        } else {
            fill = style.fill
            stroke = style.stroke
            outline = style.outline
            outline_width = style.outline_width
            stroke_width = style.stroke_width
        }

        geom = shape.pixelGeometry

        // Outline
        if (outline) {
            g2d.lineJoin = "round"
            g2d.lineWidth = outline_width
            g2d.strokeStyle = outline
            g2d.strokeRect(
                geom.x + outline_width / 2,
                geom.y + outline_width / 2,
                geom.width - outline_width,
                geom.height - outline_width,
            )
        }

        // Stroke
        if (stroke) {
            g2d.lineJoin = "miter"
            g2d.lineWidth = stroke_width
            g2d.strokeStyle = stroke
            g2d.strokeRect(
                geom.x + outline_width + stroke_width / 2,
                geom.y + outline_width + stroke_width / 2,
                geom.width - outline_width * 2 - stroke_width,
                geom.height - outline_width * 2 - stroke_width,
            )
        }

        // Fill
        if (fill) {
            g2d.lineJoin = "miter"
            g2d.lineWidth = stroke_width
            g2d.fillStyle = fill
            g2d.fillRect(
                geom.x + outline_width + stroke_width / 2,
                geom.y + outline_width + stroke_width / 2,
                geom.width - outline_width * 2 - stroke_width,
                geom.height - outline_width * 2 - stroke_width,
            )
        }
    }
}
